from django.db import models
from rest_framework import status

from common.error_definitions import CustomAPIError


class LectureManager(models.Manager):
    '''
    Manager for Lecture model

    Methods
    -------------
    check_title_duplicate(course, title, exclude_lecture=None):
        Checks if a lecture with title already exists in the course
    change_lecture_order(lecture, direction='up'):
        Moves a lecture in the list of lectures for a course
    '''

    def check_title_duplicate(self, course, title, exclude_lecture=None):
        '''
        Check if course with same title exists in course

        Parameters
        ---------------
        course : Course model instance
            The course for which the check is being performed
        title : str
            The title being checked for duplicate
        exclude_lecture : Lecture model instance
            If a lecture should be excluded while checking for duplicate.
            Default is None.
            Used during updating a lecture, when a lecture's title should
            not be checked against itself.

        Raises
        ---------------
        400 error:
            If course instance is missing
            If title string is missing
            If the proposed title is a duplicate

        Returns
        ---------------
        boolean or APIException
            Returns False is course is not duplicate or throws APIException
        '''
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
            query.get(
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
        '''
        Change sequence of lectures by moving lecture up or down in list

        Parameters
        ---------------
        lecture : Lecture model instance
            Lecture that needs to moved in the lecture list
        direction : str
            The direction of movement. Default is 'up'

        Raises
        ---------------
        400 error:
            If the first lecture in a course is moved up the list
            If the last lecture in a course is moved down the list
            If the direction is not up or down (case not sensitive)
        '''
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
