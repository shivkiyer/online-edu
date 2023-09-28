from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    '''Serializer for User model'''
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
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
