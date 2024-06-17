import pytest
from rest_framework.test import APIClient

from user_auth.models import User
from .fixtures import mock_send_verification_email, test_user

pytestmark = pytest.mark.django_db


def test_register_new_user(mock_send_verification_email):
    '''Test API to register new user'''

    client = APIClient()

    mock_send_verification_email()

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


def test_register_user_invalid_form(mock_send_verification_email, test_user):
    '''Test invalid form data for registering user'''

    client = APIClient()

    mock_send_verification_email()

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
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'Username must be a valid email'

    # Should fail because of missing password field
    api_response = client.post(
        '/api/user/register-user',
        {
            'username': 'someuser1@domain.com',
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'The password field is required'

    # Should fail because of missing username field
    api_response = client.post(
        '/api/user/register-user',
        {
            'password': 'somepass',
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'The username field is required'

    # Should fail become of missing username and password
    api_response = client.post(
        '/api/user/register-user',
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'The username field is required'

    # Should fail because of missing confirm_password field
    api_response = client.post(
        '/api/user/register-user',
        {
            'username': 'someuser1@domain.com',
            'password': 'somepass',
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'The confirm password field is required'

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
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'Passwords are not matching'

    # Should fail because of username existing
    user1 = test_user()

    api_response = client.post(
        '/api/user/register-user',
        {
            'username': 'someuser@somedomain.com',
            'password': 'somepass',
            'confirm_password': 'somepass'
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'A user with that username already exists.'
