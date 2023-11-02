from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify

from user_auth.models import User


class Course(models.Model):
    '''Course model'''
    title = models.CharField(max_length=300, unique=True)
    subtitle = models.CharField(max_length=300, null=True, blank=True)
    slug = models.SlugField(max_length=200)
    description = models.TextField()
    instructors = models.ManyToManyField(User, related_name='courses_taught')
    students = models.ManyToManyField(User)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    is_free = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    def add_instructor(self, user):
        '''Add instructors to the course'''
        if user.is_staff:
            self.instructors.add(user)
        else:
            raise Exception('Instructors have to be administrators')

    def add_students(self, user):
        '''Add students to the course'''
        self.students.add(user)


def generate_course_slug(sender, instance, *args, **kwargs):
    '''Generate slug for course'''
    if not instance.slug:
        instance.slug = slugify(instance.title)


pre_save.connect(generate_course_slug, sender=Course)
