from django.db import models
from django.contrib.auth.models import UserManager as AbstractUserManager
from rest_framework_simplejwt.tokens import RefreshToken

from common.error_definitions import Http400Error


class UserManager(AbstractUserManager):
    '''Manager for the User model'''

    def get_user_by_id(self, id, *args, **kwargs):
        try:
            return self.get(id=id, *args, **kwargs)
        except:
            raise Http400Error('User not found')

    def get_user_by_token(self, token, *args, **kwargs):
        '''Return a user object from JWT'''
        user_data = RefreshToken(token)
        try:
            user_obj = self.get_queryset().filter(
                id=int(user_data['user_id'])
            )[0]
        except:
            raise Http400Error('User not found')
        return user_obj

    def get_user_by_email(self, email):
        '''Return a user object using email'''
        try:
            return self.get(username=email)
        except:
            raise Http400Error('User not found')

    def activate_user_by_token(self, token, *args, **kwargs):
        '''Activate a user from JWT'''
        try:
            user_obj = self.get_user_by_token(token)
            user_obj.is_active = True
            user_obj.save()
            return user_obj
        except:
            raise Http400Error('User could not be activated')
