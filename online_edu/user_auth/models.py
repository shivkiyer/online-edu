from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from .managers import UserManager
from common.error_definitions import CustomAPIError


class User(AbstractUser):
    '''User model for authentication and authorization'''

    objects = UserManager()

    def save(self, *args, **kwargs):
        '''Username validation during save to db'''
        try:
            validate_email(self.username)
        except:
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=_('Username must be a valid email')
            )
        else:
            super().save(*args, **kwargs)

    def clean_fields(self, exclude=None):
        '''Ensure that username is a valid email in Admin dashboard.'''
        try:
            validate_email(self.username)
        except:
            raise ValidationError(_('Username must be a valid email'))
