from django.db import models
from rest_framework import status

from common.error_definitions import CustomAPIError


class CourseManager(models.Manager):
    '''Manager for Course model'''

    def fetch_courses(self, is_draft=False, is_archived=False):
        return self.get_queryset().filter(is_draft=is_draft, is_archived=is_archived)

    def get_course_by_slug(self, slug):
        '''Return course using slug field'''
        if slug is None:
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Slug missing'
            )
        try:
            return self.get_queryset().get(slug=slug)
        except:
            raise CustomAPIError(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Course not found'
            )
