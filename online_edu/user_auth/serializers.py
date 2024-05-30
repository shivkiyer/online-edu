from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

from .models import User
from common.error_definitions import CustomAPIError
from common.error_handling import extract_serializer_error


class UserSerializer(serializers.ModelSerializer):
    '''
    Serializer for User model

    Attributes
    --------------
    password : str

    Methods
    -------------
    save():
        Saves and returns user model instance
    create(validated_data):
        Creates new user model instance
    '''
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        error_messages={
            'blank': _('The password field is required'),
            'required': _('The password field is required')
        }
    )

    def save(self):
        '''
        Validates data and saves to model instance

        Raises
        -------------
        400 error
            Username is missing
            Username is not a valid email
            Password is missing

        Returns
        -------------
        User model instance
        '''
        if self.is_valid():
            return super().save()
        else:
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=extract_serializer_error(self.errors)
            )

    def create(self, validated_data):
        '''
        Create new user in db

        Parameters
        ---------------
        validated_data : dict

        Returns
        ---------------
        New user model instance
        '''
        new_user = User(
            username=validated_data['username']
        )
        new_user.set_password(validated_data['password'])
        # User should be inactive until email is validated
        new_user.is_active = False
        new_user.save()
        return new_user

    class Meta:
        model = User
        fields = ['username', 'password', 'is_active']
        read_only_fields = ['is_active', ]
        extra_kwargs = {
            'username': {
                'error_messages':
                {
                    'blank': _('The username field is required'),
                    'required': _('The username field is required')
                }
            }
        }


class RegisterUserSerializer(UserSerializer):
    '''
    Serializer for registering a new user

    Attributes
    ------------------
    confirm_password : str

    Methods
    ------------------
    validate(data):
        Verify that password and confirm_password match
    '''
    confirm_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        error_messages={
            'blank': _('The confirm password field is required'),
            'required': _('The confirm password field is required')
        }
    )

    def validate(self, data):
        '''Validate that password and confirm_password are the same'''
        if not data['password'] == data['confirm_password']:
            raise serializers.ValidationError(_('Passwords are not matching'))
        return data

    class Meta(UserSerializer.Meta):
        model = User
        fields = ['username', 'password', 'confirm_password', 'is_active']


class ChangePasswordSerializer(RegisterUserSerializer):
    '''
    Serializer for resetting the password of a user

    Methods
    ---------------
    update(instance, validated_data):
        Update user model instance from data
    '''

    def update(self, instance, validated_data):
        '''
        Update user password

        Parameters
        ----------------
        instance : User model instance
        validated_data : dict

        Raises
        ----------------
        400 error
            If user is not active
            If password and confirm_password are not matching
        '''
        if not instance.is_active:
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=_('User not found')
            )
        instance.set_password(validated_data.get('password'))
        instance.save()
        return instance

    class Meta(RegisterUserSerializer.Meta):
        model = User
        fields = ['password', 'confirm_password']
