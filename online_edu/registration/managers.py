from django.db import models

from common.error_definitions import Http400Error


class CourseStudentRegistrationManager(models.Manager):
    '''Student registration manager'''

    def register_student(self, user, course):
        '''Register student for course'''
        try:
            register_obj = self.get(user=user, course=course)
        except:
            return self.create(user=user, course=course)
        raise Http400Error('User is already registered')
