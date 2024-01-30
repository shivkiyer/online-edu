from django.db import models
from django.contrib.auth.models import UserManager as AbstractUserManager
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from common.error_definitions import CustomAPIError


class UserManager(AbstractUserManager):
    '''Manager for the User model'''

    def get_user_by_id(self, id, *args, **kwargs):
        try:
            return self.get(id=id, *args, **kwargs)
        except:
            raise CustomAPIError(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )

    def get_user_by_token(self, token):
        '''Return a user object from JWT'''
        user_data = RefreshToken(token)
        try:
            user_obj = self.get_queryset().filter(
                id=int(user_data['user_id'])
            )[0]
        except:
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User not found'
            )
        return user_obj

    def get_user_by_email(self, email):
        '''Return a user object using email'''
        try:
            return self.get(username=email)
        except:
            raise CustomAPIError(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )

    def activate_user_by_token(self, token):
        '''Activate a user from JWT'''
        try:
            user_obj = self.get_user_by_token(token)
            user_obj.is_active = True
            user_obj.save()
            return user_obj
        except:
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User could not be activated'
            )
