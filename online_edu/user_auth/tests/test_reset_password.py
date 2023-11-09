import pytest
from rest_framework.test import APIClient

from .fixtures import test_user, \
    mock_send_password_reset_email, \
    mock_send_mail

pytestmark = pytest.mark.django_db


def test_reset_password_end_point(test_user, mock_send_password_reset_email):
    '''Test the endpoint for sending password reset email'''

    client = APIClient()

    # Valid reset password request
    test_user.is_active = True
    test_user.save()

    api_response = client.get(
        '/api/user/reset-password/{}'.format(test_user.id),
        format='json'
    )
    assert api_response.status_code == 200


def test_reset_password_fail(test_user, mock_send_mail):
    '''Test failure of password reset email'''

    client = APIClient()

    # Inactive user
    test_user.is_active = False
    test_user.save()

    api_response = client.get(
        '/api/user/reset-password/{}'.format(test_user.id),
        format='json'
    )
    assert api_response.data == 'No user to send email to'
    assert api_response.status_code == 400

    # Non-existing user
    api_response = client.get(
        '/api/user/reset-password/{}'.format(str(test_user.id+1)),
        format='json'
    )
    assert api_response.data == 'User not found'
    assert api_response.status_code == 400
