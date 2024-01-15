from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from .error_definitions import CourseForbiddenError, CourseGenericError
from .managers import CourseManager


class Course(models.Model):
    '''Course model'''
    title = models.CharField(max_length=300, unique=True)
    subtitle = models.CharField(max_length=300, null=True, blank=True)
    slug = models.SlugField(max_length=200)
    description = models.TextField()
    instructors = models.ManyToManyField(
        'user_auth.User', related_name='courses_taught')
    students = models.ManyToManyField(
        'user_auth.User',
        blank=True,
        through='registration.CourseStudentRegistration'
    )
    price = models.DecimalField(
        default=10.99,
        max_digits=4,
        decimal_places=2
    )
    is_free = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CourseManager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.is_free and self.price <= 0:
            raise CourseGenericError('Price of a non-free course is required.')
        if self.is_free:
            self.price = 0.00
        super().save(*args, **kwargs)

    def clean_fields(self, exclude=None):
        '''Validation in admin dashboard'''
        if not self.is_free and self.price <= 0:
            raise ValidationError('Price of a non-free course is required.')

    def add_instructor(self, user):
        '''Add instructors to the course'''
        if user.is_staff:
            self.instructors.add(user)
        else:
            raise CourseForbiddenError('Instructors have to be administrators')

    def check_user_is_instructor(self, user):
        '''Check if a user is an instructor of the course'''
        instuctor_emails = [x.username for x in self.instructors.all()]
        if user and user.username in instuctor_emails:
            return True
        return False


def generate_course_slug(sender, instance, *args, **kwargs):
    '''Generate slug for course'''
    if not instance.slug:
        instance.slug = slugify(instance.title)


pre_save.connect(generate_course_slug, sender=Course)
