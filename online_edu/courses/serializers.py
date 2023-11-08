from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Course


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
            'price': {
                'error_messages': {
                    'blank': 'Course price is required',
                    'required': 'Course price is required'
                }
            }
        }
