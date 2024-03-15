from rest_framework import serializers

from .models import VideoContent


class VideoContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoContent
        fields = ['name', 'video_file']
