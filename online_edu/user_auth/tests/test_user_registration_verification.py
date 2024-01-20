import pytest
import time
from rest_framework.test import APIClient

from .fixtures import verification_token, \
    mock_send_verification_email, \
    mock_send_mail, \
    test_user

pytestmark = pytest.mark.django_db


def test_user_verification_endpoint(verification_token, test_user):
    '''Testing the verify-email endpoint'''
    client = APIClient()

    # Token with 60sec validity
    test_token1 = verification_token(60)

    api_response = client.get(
        '/api/user/verify-user/{token}'.format(
            token=test_token1
        ),
        format='json'
    )
    assert api_response.status_code == 200
    assert test_user.is_active == True

    # Token with 1sec validity - expired token test
    test_token2 = verification_token(1)
    # Sleep for 2sec
    time.sleep(2)

    api_response = client.get(
        '/api/user/verify-user/{token}'.format(
            token=test_token2
        ),
        format='json'
    )
    assert api_response.data == 'Link expired or faulty'
    assert api_response.status_code == 400

    # Tampered token test
    test_token3 = str(verification_token(60))
    test_token3 = test_token3[:-1]

    api_response = client.get(
        '/api/user/verify-user/{token}'.format(
            token=test_token3
        ),
        format='json'
    )
    assert api_response.data == 'Link expired or faulty'
    assert api_response.status_code == 400

    # Deleted user test
    test_token4 = verification_token(60)
    test_user.delete()

    api_response = client.get(
        '/api/user/verify-user/{token}'.format(
            token=test_token4
        ),
        format='json'
    )
    assert api_response.data == 'User could not be activated'
    assert api_response.status_code == 400


def test_resend_verification_endpoint(mock_send_mail, test_user):
    '''Testing endpoint for resending verification email'''
    client = APIClient()

    # Valid request
    test_user.is_active = False
    test_user.save()
    api_response = client.post(
        '/api/user/resend-verification',
        {
            'email': test_user.username
        },
        format='json'
    )
    assert api_response.status_code == 200

    # User already active
    test_user.is_active = True
    test_user.save()
    api_response = client.post(
        '/api/user/resend-verification',
        {
            'email': test_user.username
        },
        format='json'
    )
    assert api_response.data == 'User already activated'
    assert api_response.status_code == 400

    old_user_email = test_user.username
    test_user.delete()
    api_response = client.post(
        '/api/user/resend-verification',
        {
            'email': old_user_email
        },
        format='json'
    )
    assert api_response.data == 'User not found'
    assert api_response.status_code == 404
