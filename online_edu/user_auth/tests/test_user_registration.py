import pytest
from rest_framework.test import APIClient

from user_auth.models import User
from .fixtures import mock_send_verification_email

pytestmark = pytest.mark.django_db


def test_register_new_user(mock_send_verification_email):
    '''Test API to register new user'''
    client = APIClient()

    # Should result in a user created in db
    api_response = client.post(
        '/api/user/register-user',
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
        '/api/user/register-user',
        {
            'username': 'someuser',
            'password': 'somepass',
            'confirm_password': 'somepass'
        },
        format='json'
    )
    assert api_response.data == 'Username must be a valid email'
    assert api_response.status_code == 400

    # Should fail because of missing password field
    api_response = client.post(
        '/api/user/register-user',
        {
            'username': 'someuser1@domain.com',
        },
        format='json'
    )
    assert api_response.data == 'The Password Field Is Required'
    assert api_response.status_code == 400

    # Should fail because of missing username field
    api_response = client.post(
        '/api/user/register-user',
        {
            'password': 'somepass',
        },
        format='json'
    )
    assert api_response.data == 'The Username Field Is Required'
    assert api_response.status_code == 400

    # Should fail become of missing username and password
    api_response = client.post(
        '/api/user/register-user',
        format='json'
    )
    assert api_response.data == 'The Username Field Is Required'
    assert api_response.status_code == 400

    # Should fail because of username existing
    api_response = client.post(
        '/api/user/register-user',
        {
            'username': 'someuser@domain.com',
            'password': 'somepass',
            'confirm_password': 'somepass'
        },
        format='json'
    )
    assert api_response.data == 'A User With That Username Already Exists.'
    assert api_response.status_code == 400

    # Should fail because of missing confirm_password field
    api_response = client.post(
        '/api/user/register-user',
        {
            'username': 'someuser1@domain.com',
            'password': 'somepass',
        },
        format='json'
    )
    assert api_response.data == 'The Confirm Password Field Is Required'
    assert api_response.status_code == 400

    # Should fail because the passwords do not match
    api_response = client.post(
        '/api/user/register-user',
        {
            'username': 'someuser1@domain.com',
            'password': 'somepass',
            'confirm_password': 'somepass1'
        },
        format='json'
    )
    assert api_response.data == 'Passwords Are Not Matching'
    assert api_response.status_code == 400

    users_in_db = User.objects.all().count()
    assert users_in_db == 1
