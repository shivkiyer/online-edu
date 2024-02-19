from django.db import models
from rest_framework import status

from lectures.models import Lecture
from common.error_definitions import CustomAPIError


def video_file_path(instance, filename):
    '''Generate path that has course slug'''
    course = instance.lecture.course
    if course is None:
        raise CustomAPIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Associated course not found'
        )
    dir_name = ''.join(filter(str.isalnum, course.slug))
    return '{dirname}/{filename}'.format(
        dirname=dir_name,
        filename=filename
    )


class VideoContent(models.Model):
    '''Videos with every lecture'''

    lecture = models.ForeignKey(
        Lecture,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    video_file = models.FileField(upload_to=video_file_path, max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
