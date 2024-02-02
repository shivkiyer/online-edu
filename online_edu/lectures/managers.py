from django.db import models
from rest_framework import status

from common.error_definitions import CustomAPIError


class LectureManager(models.Manager):
    '''Manager for Lecture model'''

    def check_title_duplicate(self, course, title, exclude_lecture=None):
        '''Check if course with same title exists in course'''
        if course is None:
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Course must be specified to verify title'
            )
        if title is None:
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Title is required'
            )
        try:
            query = self.get_queryset()
            if exclude_lecture is not None:
                query = query.exclude(id=exclude_lecture.id)
            course_obj = query.get(
                course=course,
                title=title
            )
        except:
            return False
        raise CustomAPIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Lecture with the same title exists in the course'
        )
