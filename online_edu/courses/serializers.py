import logging
from rest_framework import serializers, status
from rest_framework.validators import UniqueValidator

from .models import Course
from common.error_definitions import CustomAPIError
from common.error_handling import extract_serializer_error

logger = logging.getLogger(__name__)


class CourseSerializer(serializers.ModelSerializer):
    '''
    Serializer for course

    Attributes
    --------------
    title : str
        Title field for course. Required and unique validators applied.

    Methods
    --------------
    validate(data) - Validates course data
    save() - saves and returns course model instance
    create(validated_data) - creates and returns course model instance
    update(self, instance, validated_data) - updates and returns course model instance
    '''

    title = serializers.CharField(
        error_messages={
            'blank': 'Course title is required',
            'required': 'Course title is required'
        },
        validators=[
            UniqueValidator(
                queryset=Course.objects.all(),
                message='A course with this title already exists'
            )
        ]
    )

    def validate(self, data):
        '''
        Validates course data.
        Sets price of free courses to be 0.

        Parameters
        -------------
        data : dict
            Course data

        Returns
        -------------
        data : dict
            Validated course data
        '''
        course_is_free = data.get('is_free', None)
        course_price = data.get('price', None)
        if course_price is not None and course_price > 0:
            data['is_free'] = False
        elif course_is_free:
            data['price'] = 0.00
        return data

    def save(self, *args, **kwargs):
        '''
        Saves course model instance to database and returns it.

        Raises
        --------------
        400 error
            If course data is not valid

        Returns
        --------------
        Course model instance
        '''
        if self.is_valid():
            return super().save(*args, **kwargs)
        else:
            err_message = extract_serializer_error(self.errors)
            logger.error(
                f'Error in saving course data - {err_message}'
            )
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=err_message
            )

    def create(self, validated_data):
        '''
        Creates a new course in database and returns model instance.

        Parameters
        --------------
        validated_data : dict
            Validated data

        Raises
        --------------
        400 error
            If course is not free but course price is missing
        403 error
            If user creating course is not an admin

        Returns
        --------------
        Course model instance
        '''
        course_is_free = validated_data.get('is_free', False)
        course_price = validated_data.get('price', None)
        if not course_is_free and (course_price is None or course_price <= 0):
            logger.error(
                f'Course {validated_data.get("title", "")} is not free but does not have valid price')
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Course price is required'
            )
        user = validated_data.get('user', None)
        if user is not None and user.is_staff:
            del validated_data['user']
            course = Course.objects.create(**validated_data)
            course.add_instructor(user)
            logger.info(
                f'Course {course.title} created successfully'
            )
            return course
        else:
            user_id = None
            if user is not None:
                user_id = user.id
            logger.critical(
                f'Non-admin user {user_id} attempting to create course'
            )
            raise CustomAPIError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Must be logged in as administrator to create a course'
            )

    def update(self, instance, validated_data):
        '''
        Updates a course in database and returns model instance.

        Parameters
        -------------
        instance : Course
            Course model instance
        validated_data : dict
            Validated course data

        Raises
        -------------
        403 error
            If a non-instructor user tries to update a course

        Returns
        -------------
        Course model instance
        '''
        user = validated_data.get('user', None)
        if user is not None and instance.check_user_is_instructor(user):
            instance.title = validated_data.get('title', instance.title)
            instance.subtitle = validated_data.get(
                'subtitle', instance.subtitle)
            instance.description = validated_data.get(
                'description', instance.description)
            instance.price = validated_data.get('price', instance.price)
            instance.is_free = validated_data.get('is_free', instance.is_free)
            instance.is_draft = validated_data.get(
                'is_draft', instance.is_draft)
            instance.is_archived = validated_data.get(
                'is_archived', instance.is_archived)
            instance.save()
            logger.info('Course {instance.title} updated successfully')
            return instance
        else:
            user_id = None
            if user is not None:
                user_id = user.id
            logger.critical(
                f'Non-admin user {user_id} attempting to create course'
            )
            raise CustomAPIError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Only an instructor of a course can update a course'
            )

    class Meta:
        model = Course
        fields = ['title', 'subtitle', 'description',
                  'price', 'is_free', 'is_draft']
        extra_kwargs = {
            'description': {
                'error_messages': {
                    'blank': 'Course description is required',
                    'required': 'Course description is required'
                }
            },
            'is_draft': {
                'write_only': True
            }
        }
