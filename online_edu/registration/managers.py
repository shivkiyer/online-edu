from django.db import models
from rest_framework import status

from common.error_definitions import CustomAPIError


class CourseStudentRegistrationManager(models.Manager):
    '''
    Student registration manager

    Methods
    --------------
    is_student_registered(user, course):
        Check is user is already registered for course
    register_student(user, course):
        Register a user for a course
    '''

    def is_student_registered(self, user, course):
        '''
        Check if a student is registered for a course

        Parameters
        -------------
        user : User model instance
        course : Course model instance

        Returns
        -------------
        boolean
            True if student is registered for a course else False
        '''
        try:
            self.get(user=user, course=course)
        except:
            return False
        return True

    def register_student(self, user, course):
        '''
        Register student for course

        Parameters
        -------------
        user : User model instance
        course : Course model instance

        Raises
        -------------
        400 error:
            If student is already registered for the course

        Returns
        -------------
        CourseStudentRegistration model instance
        '''
        if not self.is_student_registered(user=user, course=course):
            return self.create(user=user, course=course)
        raise CustomAPIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User is already registered'
        )
