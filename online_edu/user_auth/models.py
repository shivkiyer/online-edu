from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .managers import UserManager
from .error_definitions import UserGenericException


class User(AbstractUser):
    '''User model for authentication and authorization'''

    objects = UserManager()

    def save(self, *args, **kwargs):
        '''Username validation during save to db'''
        try:
            validate_email(self.username)
        except:
            raise UserGenericException('Username must be a valid email')
        else:
            super().save(*args, **kwargs)

    def clean_fields(self, exclude=None):
        '''Ensure that username is a valid email in Admin dashboard.'''
        try:
            validate_email(self.username)
        except:
            raise ValidationError('Username must be a valid email')
