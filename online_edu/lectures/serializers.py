from rest_framework import serializers
from rest_framework import status

from common.error_definitions import CustomAPIError
from common.error_handling import extract_serializer_error
from .models import Lecture


class LectureSerializer(serializers.ModelSerializer):
    '''Serializer for Lecture model'''

    def save(self, *args, **kwargs):
        if self.is_valid():
            return super().save(*args, **kwargs)
        else:
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=extract_serializer_error(self.errors)
            )

    def check_user_is_instructor(self, course, user):
        if user is None:
            raise CustomAPIError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Must be logged in as an instructor to create lectures'
            )
        if not course.check_user_is_instructor(user):
            raise CustomAPIError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Must be an instructor of the course to create lectures'
            )
        return True

    def update(self, instance, validated_data):
        user = validated_data.get('user', None)
        course = validated_data.get('course', None)
        if self.check_user_is_instructor(course, user):
            del validated_data['user']
            del validated_data['course']
        if not Lecture.objects.check_title_duplicate(
            course,
            validated_data.get('title'),
            exclude_course=instance
        ):
            instance.title = validated_data.get('title', instance.title)
            instance.description = validated_data.get(
                'description', instance.description)
            instance.save()
            return instance

    def create(self, validated_data):
        user = validated_data.get('user', None)
        course = validated_data.get('course', None)
        if self.check_user_is_instructor(course, user):
            del validated_data['user']
            del validated_data['course']
        if not Lecture.objects.check_title_duplicate(
            course,
            validated_data.get('title'),
        ):
            return Lecture.objects.create(
                **validated_data,
                course=course
            )

    class Meta:
        model = Lecture
        fields = ['title', 'description']
        extra_kwargs = {
            'title': {
                'error_messages': {
                    'required': 'The title of a lecture is required',
                    'blank': 'The title of a lecture is required'
                }
            }
        }
