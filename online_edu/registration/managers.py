from django.db import models

from courses.error_definitions import CourseGenericError


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
            raise CourseGenericError('User is already registered')

        return self.create(user=user, course=course)
