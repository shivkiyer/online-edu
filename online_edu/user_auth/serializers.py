from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import User
from .error_definitions import UserGenericException


class UserSerializer(serializers.ModelSerializer):
    '''Serializer for User model'''
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        error_messages={
            'blank': 'The password field is required',
            'required': 'The password field is required'
        }
    )

    def create(self, validated_data):
        '''Create new user in db'''
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
                    'blank': 'The username field is required',
                    'required': 'The username field is required'
                }
            }
        }


class RegisterUserSerializer(UserSerializer):
    '''Serializer for registering a new user'''
    confirm_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        error_messages={
            'blank': 'The confirm password field is required',
            'required': 'The confirm password field is required'
        }
    )

    def validate(self, data):
        '''Validate that password and confirm_password are the same'''
        if not data['password'] == data['confirm_password']:
            raise serializers.ValidationError('Passwords are not matching')
        return data

    class Meta(UserSerializer.Meta):
        model = User
        fields = ['username', 'password', 'confirm_password', 'is_active']


class ChangePasswordSerializer(RegisterUserSerializer):
    '''Serializer for resetting the password of a user'''

    def update(self, instance, validated_data):
        '''Update user password'''
        if not instance.is_active:
            raise UserGenericException('User not found')
        instance.set_password(validated_data.get('password'))
        instance.save()
        return instance

    class Meta(RegisterUserSerializer.Meta):
        model = User
        fields = ['password', 'confirm_password']
