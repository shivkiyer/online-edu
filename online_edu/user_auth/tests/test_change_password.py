import pytest
import time
from django.contrib.auth import authenticate
from rest_framework.test import APIClient

from .fixtures import verification_token, \
    mock_send_verification_email, \
    test_user

pytestmark = pytest.mark.django_db


def test_password_change_endpoint(verification_token, test_user):
    '''Testing the password change endpoint'''
    client = APIClient()

    user1 = test_user()

    # Token with 60sec validity
    test_token1 = verification_token(user1, 60)

    # Valid password change request
    api_response = client.post(
        '/api/user/change-password/{token}'.format(
            token=test_token1
        ),
        {
            'password': 'newpassword',
            'confirm_password': 'newpassword'
        },
        format='json'
    )
    assert api_response.status_code == 200
    check_user = authenticate(
        username=user1.username,
        password='somepassword'
    )
    assert check_user == None
    check_user = authenticate(
        username=user1.username,
        password='newpassword'
    )
    assert check_user != None
    assert check_user.username == user1.username

    # Password field blank
    api_response = client.post(
        '/api/user/change-password/{token}'.format(
            token=test_token1
        ),
        {
            'password': '',
            'confirm_password': '',
        },
        format='json'
    )
    assert api_response.data['detail'].lower(
    ) == 'the password field is required'
    assert api_response.status_code == 400

    # Password field missing
    api_response = client.post(
        '/api/user/change-password/{token}'.format(
            token=test_token1
        ),
        {
            'confirm_password': 'newpassword',
        },
        format='json'
    )
    assert api_response.data['detail'].lower(
    ) == 'the password field is required'
    assert api_response.status_code == 400

    # Confirm password field missing
    api_response = client.post(
        '/api/user/change-password/{token}'.format(
            token=test_token1
        ),
        {
            'password': 'newpassword',
        },
        format='json'
    )
    assert api_response.data['detail'].lower(
    ) == 'the confirm password field is required'
    assert api_response.status_code == 400

    # Password not matching
    api_response = client.post(
        '/api/user/change-password/{token}'.format(
            token=test_token1
        ),
        {
            'password': 'newpassword',
            'confirm_password': 'newpassword1'
        },
        format='json'
    )
    assert api_response.data['detail'].lower() == 'passwords are not matching'
    assert api_response.status_code == 400

    # Token with 1sec validity - expired token test
    test_token2 = verification_token(user1, 1)
    # Sleep for 2sec
    time.sleep(2)

    api_response = client.post(
        '/api/user/change-password/{token}'.format(
            token=test_token2
        ),
        {
            'password': 'newpassword',
            'confirm_password': 'newpassword'
        },
        format='json'
    )
    assert api_response.data['detail'] == 'Link expired or faulty'
    assert api_response.status_code == 400

    # Tampered token test
    test_token3 = str(verification_token(user1, 60))
    test_token3 = test_token3[:-1]

    api_response = client.post(
        '/api/user/change-password/{token}'.format(
            token=test_token2
        ),
        {
            'password': 'newpassword',
            'confirm_password': 'newpassword'
        },
        format='json'
    )
    assert api_response.data['detail'] == 'Link expired or faulty'
    assert api_response.status_code == 400

    # Inactive user test
    user1.is_active = False
    user1.save()
    api_response = client.post(
        '/api/user/change-password/{token}'.format(
            token=test_token1
        ),
        {
            'password': 'newpassword',
            'confirm_password': 'newpassword'
        },
        format='json'
    )
    assert api_response.data['detail'] == 'User not found'
    assert api_response.status_code == 400

    # Deleted user test
    user1.is_active = True
    user1.save()
    user1.delete()

    api_response = client.post(
        '/api/user/change-password/{token}'.format(
            token=test_token1
        ),
        {
            'password': 'newpassword',
            'confirm_password': 'newpassword'
        },
        format='json'
    )
    assert api_response.data['detail'] == 'User not found'
    assert api_response.status_code == 400
