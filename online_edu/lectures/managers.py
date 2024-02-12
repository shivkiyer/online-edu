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

    def change_lecture_order(self, lecture, direction='up'):
        '''Change sequence of lectures'''
        direction = direction.lower()
        if lecture.seq_no == 1 and direction == 'up':
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Lecture is already the first in the course'
            )
        course = lecture.course
        no_of_lectures = self.get_queryset().filter(course=course).count()
        if lecture.seq_no == no_of_lectures and direction == 'down':
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Lecture is already the last in the course'
            )
        if direction == 'up':
            other_seq_no = lecture.seq_no - 1
        elif direction == 'down':
            other_seq_no = lecture.seq_no + 1
        else:
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Direction in which the lecture needs to be moved can be up or down'
            )
        prev_lecture = self.get_queryset().get(
            course=course,
            seq_no=other_seq_no
        )
        lecture.seq_no, prev_lecture.seq_no = prev_lecture.seq_no, lecture.seq_no
        lecture.save()
        prev_lecture.save()
