from rest_framework import serializers, status
from rest_framework.validators import UniqueValidator

from .models import Course
from common.error_definitions import CustomAPIError
from common.error_handling import extract_serializer_error


class CourseSerializer(serializers.ModelSerializer):
    '''Serializer for course'''

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
        course_is_free = data.get('is_free', None)
        course_price = data.get('price', None)
        if course_price is not None and course_price > 0:
            data['is_free'] = False
        elif course_is_free:
            data['price'] = 0.00
        return data

    def save(self, *args, **kwargs):
        if self.is_valid():
            return super().save(*args, **kwargs)
        else:
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=extract_serializer_error(self.errors)
            )

    def create(self, validated_data):
        course_is_free = validated_data.get('is_free', False)
        course_price = validated_data.get('price', None)
        if not course_is_free and (course_price is None or course_price <= 0):
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Course price is required'
            )
        user = validated_data.get('user', None)
        if user is not None and user.is_staff:
            del validated_data['user']
            course = Course.objects.create(**validated_data)
            course.add_instructor(user)
            return course
        else:
            raise CustomAPIError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Must be logged in as administrator to create a course'
            )

    def update(self, instance, validated_data):
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
            return instance
        else:
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
