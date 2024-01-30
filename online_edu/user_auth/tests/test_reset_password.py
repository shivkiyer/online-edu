import pytest
from rest_framework.test import APIClient

from .fixtures import test_user, \
    mock_send_password_reset_email, \
    mock_send_mail

pytestmark = pytest.mark.django_db


def test_reset_password_end_point(test_user, mock_send_password_reset_email):
    '''Test the endpoint for sending password reset email'''

    client = APIClient()

    user1 = test_user()

    # Valid reset password request
    user1.is_active = True
    user1.save()

    api_response = client.post(
        '/api/user/reset-password',
        {
            'email': user1.username
        },
        format='json'
    )
    assert api_response.status_code == 200


def test_reset_password_fail(test_user, mock_send_mail):
    '''Test failure of password reset email'''

    client = APIClient()

    user1 = test_user()

    # Inactive user
    user1.is_active = False
    user1.save()

    api_response = client.post(
        '/api/user/reset-password',
        {
            'email': user1.username
        },
        format='json'
    )
    assert api_response.data['detail'] == 'No user to send email to'
    assert api_response.status_code == 400

    # Non-existing user
    api_response = client.post(
        '/api/user/reset-password',
        {
            'email': 'someemail@gmail.com'
        },
        format='json'
    )
    assert api_response.data['detail'] == 'User not found'
    assert api_response.status_code == 404
