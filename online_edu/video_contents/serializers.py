from rest_framework import serializers

from .models import VideoContent


class VideoContentSerializer(serializers.ModelSerializer):
    '''
    Serializer for model VideoContent
    '''
    video_file_path = serializers.ReadOnlyField()

    class Meta:
        model = VideoContent
        fields = ['name', 'video_file_path']
