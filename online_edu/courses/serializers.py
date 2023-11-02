from rest_framework import serializers

from .models import Course


class CourseSerializer(serializers.ModelSerializer):
    '''Serializer for course'''

    class Meta:
        model = Course
        fields = ['title', 'subtitle', 'description', 'price', 'is_free',]
