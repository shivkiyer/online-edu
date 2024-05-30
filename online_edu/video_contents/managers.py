from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from common.error_definitions import CustomAPIError


class VideoContentManager(models.Manager):
    '''
    Video Content Manager

    Methods
    ------------
    is_video_name_unique(name):
        Checks if name of video is unique
    '''

    def is_video_name_unique(self, name):
        '''
        Checks if name of video is unique

        Parameters
        ------------
        name : str
            Name of video

        Raises
        ------------
        400 error:
            If the video name is a duplicate

        Returns
        ------------
        bool
        '''

        try:
            self.get_queryset().get(name=name)
        except:
            return True
        raise CustomAPIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_('Another video with the same name already exists')
        )
