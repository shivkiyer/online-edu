from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken


class UserManager(BaseUserManager):
    '''Manager for the User model'''

    def get_user_by_token(self, token, *args, **kwargs):
        '''Return a user object from JWT'''
        user_data = RefreshToken(token)
        try:
            user_obj = self.get_queryset().filter(
                id=int(user_data['user_id'])
            )[0]
        except:
            raise ValidationError('User not found')
        return user_obj

    def activate_user_by_token(self, token, *args, **kwargs):
        '''Activate a user from JWT'''
        try:
            user_obj = self.get_user_by_token(token)
            user_obj.is_active = True
            user_obj.save()
            return user_obj
        except:
            raise ValidationError('User could not be activated')
