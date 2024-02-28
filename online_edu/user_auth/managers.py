from django.db import models
from django.contrib.auth.models import UserManager as AbstractUserManager
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from common.error_definitions import CustomAPIError


class UserManager(AbstractUserManager):
    '''
    Manager for the User model

    Methods
    ---------------
    get_user_by_id(id, *args, **kwargs):
        Return user model instance by id column
    get_user_by_token(token):
        Return user model instance from JWT
    get_user_by_email(email):
        Return user model instance from email
    activate_user_by_token(token):
        Activate a user account from a JWT
    '''

    def get_user_by_id(self, id, *args, **kwargs):
        '''
        Fetch user by db Id

        Parameters
        -------------
        id : int

        Raises
        -------------
        404 error
            User not found

        Returns
        -------------
        User model instance
        '''
        try:
            return self.get(id=id, *args, **kwargs)
        except:
            raise CustomAPIError(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )

    def get_user_by_token(self, token):
        '''
        Return a user object from JWT

        Parameters
        -------------
        token : str
            JWT

        Raises
        -------------
        400 error
            User not found

        Returns
        -------------
        User model instance
        '''
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
        '''
        Return a user object using email

        Parameters
        -------------
        email : str

        Raises
        -------------
        404 error
            User not found

        Returns
        -------------
        User model instance
        '''
        try:
            return self.get(username=email)
        except:
            raise CustomAPIError(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )

    def activate_user_by_token(self, token):
        '''
        Activate a user from JWT

        Parameters
        -------------
        token : str
            JWT

        Raises
        -------------
        400 error
            User could not be activated
        '''
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
