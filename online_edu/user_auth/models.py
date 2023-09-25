from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class User(AbstractUser):
    '''User model for authentication and authorization'''

    def save(self, *args, **kwargs):
        '''Username validation during save to db'''
        try:
            validate_email(self.username)
        except:
            raise ValidationError('Username must be a valid email')
        else:
            super().save(*args, **kwargs)

    def clean_fields(self, exclude=None):
        '''Ensure that username is a valid email in Admin dashboard.'''
        try:
            validate_email(self.username)
        except:
            raise ValidationError('Username must be a valid email')
