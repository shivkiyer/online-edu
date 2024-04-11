import logging
from rest_framework import serializers
from rest_framework import status

from common.error_definitions import CustomAPIError
from common.error_handling import extract_serializer_error
from .models import Lecture
from video_contents.serializers import VideoContentSerializer

logger = logging.getLogger(__name__)


class LectureSerializer(serializers.ModelSerializer):
    '''
    Serializer for Lecture model

    Methods
    -------------
    save():
        Saves the serializer data in a lecture model instance
    validate(data):
        Validates serializer data
    check_user_is_instructor(course, user):
        Checks if a user is an instructor for a course
    update(instance, validated_data):
        Updates a lecture model instance from serializer data
    create(validated_data):
        Creates a new lecture model instance from serializer data
    '''

    def save(self, *args, **kwargs):
        '''
        Validates serializer data and returns model instance

        Raises
        --------------
        400 error:
            If serializer data has errors

        Returns
        --------------
        Lecture model instance
        '''
        if self.is_valid():
            return super().save(*args, **kwargs)
        else:
            err_message = extract_serializer_error(self.errors)
            logger.error(f'Error in creating lecture - {err_message}')
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=err_message
            )

    def validate(self, data):
        '''
        Validates serializer data

        Parameters
        ----------------
        data : dict
            Serializer data

        Raises
        ----------------
        400 error:
            If serializer data is empty

        Returns
        ----------------
        data : dict
            Serializer data if it is valid
        '''
        if not data:
            logger.critical('Empty lecture request')
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Empty request body'
            )
        return data

    def check_user_is_instructor(self, course, user):
        '''
        Check if user is an instructor of a course

        Parameters
        --------------
        course : Course model instance
            Course that the lecture belongs to
        user :  User model instance
            User being verified

        Raises
        --------------
        403 error:
            If user credentials are not passed
            If user is not an instructor of the course

        Returns
        --------------
        boolean
            True if the user is an instructor of the course
        '''
        if user is None:
            logger.critical(
                'Attempt to create or update lecture without credentials'
            )
            raise CustomAPIError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Must be logged in as an instructor to create or update lectures'
            )
        if not course.check_user_is_instructor(user):
            logger.critical(
                f'User {user.id} not instructor of course trying to create or update lecture'
            )
            raise CustomAPIError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Must be an instructor of the course to create or update lectures'
            )
        return True

    def update(self, instance, validated_data):
        '''
        Updates a lecture model instance with validated data

        Parameters
        --------------
        instance : Lecture model instance
            The lecture that is being updated
        validated_data : dict
            The validated serializer data

        Raises
        --------------
        400 error:
            If serializer data is empty
            If new title is same as another lecture in the course
        403 error:
            User not logged in
            User not admin
            User not an instructor

        Returns
        -------------
        Updated lecture model instance
        '''
        user = validated_data.get('user', None)
        course = validated_data.get('course', None)
        title_data = validated_data.get('title', None)
        if self.check_user_is_instructor(course, user):
            del validated_data['user']
            del validated_data['course']
        if title_data is not None and not Lecture.objects.check_title_duplicate(
            course,
            validated_data.get('title'),
            exclude_lecture=instance
        ):
            instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.save()
        logger.info(
            f'Lecture {instance.title} in course {course.title} updated by user {user.id} successfully'
        )
        return instance

    def create(self, validated_data):
        '''
        Creates a lecture model instance from validated data

        Parameters
        ---------------
        validated_data : dict
            Data verified by validate method and field validation methods

        Raises
        ---------------
        400 error:
            If title is missing
            If title is duplicate
        403 error:
            If user credentials are not provided
            If user is not admin
            If user is not an instructor
        '''
        user = validated_data.get('user', None)
        course = validated_data.get('course', None)
        if self.check_user_is_instructor(course, user):
            del validated_data['user']
            del validated_data['course']
        if not Lecture.objects.check_title_duplicate(
            course,
            validated_data.get('title'),
        ):
            logger.info(
                f'Lecture {validated_data.get("title", None)} in course {course.title} created by user {user.id} successfully'
            )
            return Lecture.objects.create(
                **validated_data,
                course=course
            )

    class Meta:
        model = Lecture
        fields = ['id', 'title', 'description', 'seq_no']
        extra_kwargs = {
            'id': {
                'read_only': True
            },
            'seq_no': {
                'read_only': True
            },
            'title': {
                'error_messages': {
                    'required': 'The title of a lecture is required',
                    'blank': 'The title of a lecture is required'
                }
            }
        }


class LectureDetailSerializer(serializers.ModelSerializer):
    '''
    Serializer for detail view of Lecture including related videos
    '''

    videos = VideoContentSerializer(many=True, read_only=True)

    class Meta:
        model = Lecture
        fields = ['id', 'title', 'description', 'seq_no', 'videos']
