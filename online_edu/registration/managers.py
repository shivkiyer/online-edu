from django.db import models
from rest_framework import status

from common.error_definitions import CustomAPIError


class CourseStudentRegistrationManager(models.Manager):
    '''Student registration manager'''

    def register_student(self, user, course):
        '''Register student for course'''
        try:
            register_obj = self.get(user=user, course=course)
        except:
            return self.create(user=user, course=course)
        raise CustomAPIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User is already registered'
        )
