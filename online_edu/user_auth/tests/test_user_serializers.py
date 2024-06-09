import pytest
from django.contrib.auth import authenticate

from user_auth.serializers import UserSerializer, \
    RegisterUserSerializer, \
    ChangePasswordSerializer
from user_auth.models import User
from .fixtures import test_user

pytestmark = pytest.mark.django_db


def test_user_serializer():
    '''Testing base UserSerializer'''

    # Success
    serializer = UserSerializer(data={
        'username': 'someuser@domain.com',
        'password': 'somepassword'
    })
    serializer.save()

    assert 'username' in serializer.data
    assert 'is_active' in serializer.data
    assert 'password' not in serializer.data
    assert User.objects.count() == 1


def test_user_serializer_invalid_data(test_user):
    '''Testing base UserSerializer handling invalid data'''

    # Blank user serializer should through username is missing
    serializer = UserSerializer(data={})
    with pytest.raises(Exception) as e:
        serializer.save()
    assert str(e.value) == 'The username field is required'

    # Missing password field
    serializer = UserSerializer(data={
        'username': 'someuser'
    })
    with pytest.raises(Exception) as e:
        serializer.save()
    assert str(e.value) == 'The password field is required'

    # Username not a valid email
    serializer = UserSerializer(data={
        'username': 'someuser',
        'password': 'somepassword'
    })
    with pytest.raises(Exception) as e:
        serializer.save()
    assert str(e.value) == 'Username must be a valid email'

    # Create test user someuser@somedomain.com
    user1 = test_user()

    # Duplicate username error
    serializer = UserSerializer(data={
        'username': 'someuser@somedomain.com',
        'password': 'somepassword'
    })
    with pytest.raises(Exception) as e:
        serializer.save()
    assert str(e.value) == 'A user with that username already exists.'


def test_user_register_serializer():
    '''Testing the RegisterUserSerializer'''

    # Success
    serializer = RegisterUserSerializer(data={
        'username': 'someuser@domain.com',
        'password': 'somepassword',
        'confirm_password': 'somepassword'
    })
    serializer.save()
    assert 'username' in serializer.data
    assert 'is_active' in serializer.data
    assert 'password' not in serializer.data
    assert User.objects.count() == 1


def test_user_register_serializer_invalid_data(test_user):
    '''Testing the RegisterUserSerializer handling invalid data'''

    # Blank user serializer should through username is missing
    serializer = RegisterUserSerializer(data={})
    with pytest.raises(Exception) as e:
        serializer.save()
    assert str(e.value) == 'The username field is required'

    # Missing password field
    serializer = RegisterUserSerializer(data={
        'username': 'someuser'
    })
    with pytest.raises(Exception) as e:
        serializer.save()
    assert str(e.value) == 'The password field is required'

    # Confirm password is missing
    serializer = RegisterUserSerializer(data={
        'username': 'someuser',
        'password': 'somepassword'
    })
    with pytest.raises(Exception) as e:
        serializer.save()
    assert str(e.value) == 'The confirm password field is required'

    # Username not a valid email
    serializer = RegisterUserSerializer(data={
        'username': 'someuser',
        'password': 'somepassword',
        'confirm_password': 'somepassword'
    })
    with pytest.raises(Exception) as e:
        serializer.save()
    assert str(e.value) == 'Username must be a valid email'

    # Password not matching
    serializer = RegisterUserSerializer(data={
        'username': 'someuser',
        'password': 'somepassword',
        'confirm_password': 'somepassword1'
    })
    with pytest.raises(Exception) as e:
        serializer.save()
    assert str(e.value) == 'Passwords are not matching'

    # Creating test user someuser@somedomain.com
    user1 = test_user()

    # Duplicate username error
    serializer = RegisterUserSerializer(data={
        'username': 'someuser@somedomain.com',
        'password': 'somepassword'
    })
    with pytest.raises(Exception) as e:
        serializer.save()
    assert str(e.value) == 'A user with that username already exists.'


def test_change_password_serializer(test_user):
    '''Testing ChangePasswordSerializer'''

    user1 = test_user(
        'someuser@domain.com',
        'somepassword',
        False
    )
    user1.save()

    # Success
    serializer = ChangePasswordSerializer(user1, data={
        'password': 'anotherpassword',
        'confirm_password': 'anotherpassword'
    })
    serializer.save()

    # Old password should not work
    check_user = authenticate(
        username='someuser@domain.com',
        password='somepassword'
    )
    assert check_user is None

    # New password should work
    check_user = authenticate(
        username='someuser@domain.com',
        password='anotherpassword'
    )
    assert check_user is not None


def test_change_password_serializer_invalid_data(test_user):
    '''Testing ChangePasswordSerializer handling invalid data'''

    user1 = test_user(
        'someuser@domain.com',
        'somepassword',
        False
    )
    # Making user inactive
    user1.is_active = False
    user1.save()

    # Missing password field
    serializer = ChangePasswordSerializer(user1, data={})
    with pytest.raises(Exception) as e:
        serializer.save()
    assert str(e.value) == 'The password field is required'

    # Missing confirm_password field
    serializer = ChangePasswordSerializer(user1, data={
        'password': 'anotherpassword'
    })
    with pytest.raises(Exception) as e:
        serializer.save()
    assert str(e.value) == 'The confirm password field is required'

    # Passwords not matching
    serializer = ChangePasswordSerializer(user1, data={
        'password': 'anotherpassword',
        'confirm_password': 'somepassword'
    })
    with pytest.raises(Exception) as e:
        serializer.save()
    assert str(e.value) == 'Passwords are not matching'

    # User not active
    serializer = ChangePasswordSerializer(user1, data={
        'password': 'anotherpassword',
        'confirm_password': 'anotherpassword'
    })
    with pytest.raises(Exception) as e:
        serializer.save()
    assert str(e.value) == 'User not found'
