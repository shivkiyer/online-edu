from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Course
from .error_definitions import CourseGenericError, CourseForbiddenError


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
        course_is_free = data.get('is_free', False)
        course_price = data.get('price', None)
        if course_is_free:
            data['price'] = 0.00
        elif course_price is None or course_price <= 0:
            raise CourseGenericError('Course price is required')
        return data

    def create(self, validated_data):
        user = validated_data.get('user', None)
        if user is not None and user.is_staff:
            del validated_data['user']
            course = Course.objects.create(**validated_data)
            course.add_instructor(user)
            return course
        else:
            raise CourseForbiddenError(
                'Must be logged in as administrator to create a course'
            )

    class Meta:
        model = Course
        fields = ['title', 'subtitle', 'description', 'price', 'is_free',]
        extra_kwargs = {
            'description': {
                'error_messages': {
                    'blank': 'Course description is required',
                    'required': 'Course description is required'
                }
            },
        }
