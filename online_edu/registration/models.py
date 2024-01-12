from django.db import models


class CourseStudentRegistration(models.Model):
    '''Registration of a student in a course'''
    user = models.ForeignKey(
        'user_auth.User',
        null=True,
        on_delete=models.SET_NULL
    )
    course = models.ForeignKey(
        'courses.Course',
        null=True,
        on_delete=models.SET_NULL
    )
    registered_at = models.DateTimeField(auto_now_add=True)
