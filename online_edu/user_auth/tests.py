import pytest
from rest_framework.test import APIClient

from .models import User

pytestmark = pytest.mark.django_db


def test_username_only_email():
    '''Test that the username can only be a valid email'''

    # Passing test with valid email
    user1 = User(username='someuser@domain.com')
    user1.set_password('somepasswordfortest')
    user1.save()
    users_in_db = User.objects.all().count()
    assert users_in_db == 1

    # Failing test with normal text instead of email
    with pytest.raises(Exception):
        user2 = User(username='someuser')
        user2.set_password('someotherpassword')
        user2.save()

    users_in_db = User.objects.all().count()
    assert users_in_db == 1


def test_register_new_user():
    '''Test API to register new user'''
    client = APIClient()

    # Should result in a user created in db
    api_response = client.post(
        '/user/register-user',
        {
            'username': 'someuser@domain.com',
            'password': 'somepass',
            'confirm_password': 'somepass'
        },
        format='json'
    )
    assert api_response.status_code == 201
    assert api_response.data['username'] == 'someuser@domain.com'
    assert hasattr(api_response.data, 'password') == False
    assert api_response.data['is_active'] == False

    users_in_db = User.objects.all().count()
    assert users_in_db == 1

    # Should fail model validation
    api_response = client.post(
        '/user/register-user',
        {
            'username': 'someuser',
            'password': 'somepass'
        },
        format='json'
    )
    assert api_response.status_code == 400

    # Should fail because of missing password field
    api_response = client.post(
        '/user/register-user',
        {
            'username': 'someuser@domain.com',
        },
        format='json'
    )
    assert api_response.status_code == 400

    # Should fail because of missing username field
    api_response = client.post(
        '/user/register-user',
        {
            'password': 'somepass',
        },
        format='json'
    )
    assert api_response.status_code == 400

    # Should fail become of missing username and password
    api_response = client.post(
        '/user/register-user',
        format='json'
    )
    assert api_response.status_code == 400

    # Should fail because of missing confirm_password field
    api_response = client.post(
        '/user/register-user',
        {
            'username': 'someuser@domain.com',
            'password': 'somepass',
        },
        format='json'
    )
    assert api_response.status_code == 400

    # Should fail because the passwords do not match
    api_response = client.post(
        '/user/register-user',
        {
            'username': 'someuser1@domain.com',
            'password': 'somepass',
            'confirm_password': 'somepass1'
        },
        format='json'
    )
    assert api_response.status_code == 400

    users_in_db = User.objects.all().count()
    assert users_in_db == 1
