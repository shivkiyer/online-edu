from django.db import models


class Lecture(models.Model):
    '''Lecture model'''

    course = models.ForeignKey(
        'courses.Course',
        models.SET_NULL,
        null=True
    )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
