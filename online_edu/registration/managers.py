from django.db import models

from common.error_definitions import Http400Error


class CourseStudentRegistrationManager(models.Manager):
    '''Student registration manager'''

    def register_student(self, user, course):
        '''Register student for course'''

        register_obj = None
        try:
            register_obj = self.get(user=user, course=course)
        except:
            pass
        if register_obj is not None:
            raise Http400Error('User is already registered')

        return self.create(user=user, course=course)
