from django.db import models
from django.db.models.signals import pre_save

from .managers import LectureManager


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
    seq_no = models.IntegerField(default=0)

    objects = LectureManager()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['seq_no']


def generate_sequence_no(sender, instance, *args, **kwargs):
    '''Generate sequence number for a lecture in a course'''
    if not instance.seq_no:
        course = instance.course
        last_lecture_no = sender.objects.filter(course=course).count()
        instance.seq_no = last_lecture_no + 1


pre_save.connect(generate_sequence_no, sender=Lecture)
