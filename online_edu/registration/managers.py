from django.db import models
from rest_framework import status

from common.error_definitions import CustomAPIError


class CourseStudentRegistrationManager(models.Manager):
    '''Student registration manager'''

    def is_student_registered(self, user, course):
        '''Check if a student is registered for a course'''
        try:
            self.get(user=user, course=course)
        except:
            return False
        return True

    def register_student(self, user, course):
        '''Register student for course'''
        if not self.is_student_registered(user=user, course=course):
            return self.create(user=user, course=course)
        raise CustomAPIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User is already registered'
        )
