from django.db import models
from django.db.models.signals import pre_save

from .managers import LectureManager


class Lecture(models.Model):
    '''
    Lecture model

    Attributes
    ----------------
    title : str
        Title of lecture
    description : str (optional)
        Description of lecture
    videos : ManyToMany relationship
        References to VideoContent model instances
    created_at : Datetime
        Autogenerated when model instance is created
    updated_at: Datetime
        Autoupdated when model instance is updated
    seq_no : int
        The position of the lecture in the lecture list of a course
    '''

    course = models.ForeignKey(
        'courses.Course',
        models.SET_NULL,
        null=True
    )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    videos = models.ManyToManyField(
        'video_contents.VideoContent',
        related_name='lectures'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    seq_no = models.IntegerField(default=0)

    objects = LectureManager()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['seq_no']


def generate_sequence_no(sender, instance, *args, **kwargs):
    '''
    Generate sequence number for a lecture in a course

    Parameters
    ------------------
    sender : Model class (Lecture)
        Class that causes the signal to call the fuction
    instance : model instance (Lecture)
        The instance that is being saved
    '''
    if not instance.seq_no:
        course = instance.course
        last_lecture_no = sender.objects.filter(course=course).count()
        instance.seq_no = last_lecture_no + 1


pre_save.connect(generate_sequence_no, sender=Lecture)
