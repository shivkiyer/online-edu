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

    user1 = test_user()

    # Token with 60sec validity
    test_token1 = verification_token(user1, 60)

    api_response = client.get(
        f'/api/user/verify-user/{test_token1}',
        format='json'
    )
    assert api_response.status_code == 200
    assert user1.is_active == True


def test_user_verification_failed_token(verification_token, test_user):
    '''Testing invalid or expired tokens in user verification'''

    client = APIClient()

    user1 = test_user()

    # Token with 1sec validity - expired token test
    test_token2 = verification_token(user1, 1)
    # Sleep for 2sec
    time.sleep(2)

    api_response = client.get(
        f'/api/user/verify-user/{test_token2}',
        format='json'
    )
    assert api_response.data['detail'] == 'Link expired or faulty'
    assert api_response.status_code == 400

    # Tampered token test
    test_token3 = str(verification_token(user1, 60))
    test_token3 = test_token3[:-1]

    api_response = client.get(
        f'/api/user/verify-user/{test_token3}',
        format='json'
    )
    assert api_response.data['detail'] == 'Link expired or faulty'
    assert api_response.status_code == 400

    # Deleted user test
    test_token4 = verification_token(user1, 60)
    user1.delete()

    api_response = client.get(
        f'/api/user/verify-user/{test_token4}',
        format='json'
    )
    assert api_response.data['detail'] == 'User could not be activated'
    assert api_response.status_code == 400


def test_resend_verification_endpoint(mock_send_mail, test_user):
    '''Testing endpoint for resending verification email'''

    client = APIClient()

    user1 = test_user()

    # Valid request
    user1.is_active = False
    user1.save()
    api_response = client.post(
        '/api/user/resend-verification',
        {
            'email': user1.username
        },
        format='json'
    )
    assert api_response.status_code == 200


def test_resend_verification_invalid_user(mock_send_mail, test_user):
    '''Testing that only inactive users can verify'''

    client = APIClient()

    user1 = test_user()

    # User already active
    user1.is_active = True
    user1.save()
    api_response = client.post(
        '/api/user/resend-verification',
        {
            'email': user1.username
        },
        format='json'
    )
    assert api_response.data['detail'] == 'User already activated'
    assert api_response.status_code == 400

    old_user_email = user1.username
    user1.delete()
    api_response = client.post(
        '/api/user/resend-verification',
        {
            'email': old_user_email
        },
        format='json'
    )
    assert api_response.data['detail'] == 'User not found'
    assert api_response.status_code == 404
