import pytest
from datetime import timedelta
import time
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from user_auth.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def test_user():
    '''Create sample user for test'''
    sample_user = User.objects.create(username='someuser@somedomain.com')
    sample_user.set_password('somepassword')
    sample_user.save()
    return sample_user


@pytest.fixture
def verification_token(test_user):
    '''Creating tokens with JWT'''

    def _create_token(exp_time):
        '''Token with variable expiry time'''
        verification_token = RefreshToken.for_user(test_user)
        verification_token.set_exp(
            from_time=verification_token.current_time,
            lifetime=timedelta(seconds=exp_time)
        )
        return verification_token

    return _create_token


def test_user_verification_endpoint(verification_token, test_user):
    '''Testing the verify-email endpoint'''
    client = APIClient()

    # Token with 60sec validity
    test_token1 = verification_token(60)

    api_response = client.get(
        '/user/verify-user/{token}'.format(
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
        '/user/verify-user/{token}'.format(
            token=test_token2
        ),
        format='json'
    )
    assert api_response.status_code == 400

    # Tampered token test
    test_token3 = str(verification_token(60))
    test_token3 = test_token3[:-1]

    api_response = client.get(
        '/user/verify-user/{token}'.format(
            token=test_token3
        ),
        format='json'
    )
    assert api_response.status_code == 400

    # Deleted user test
    test_token4 = verification_token(60)
    test_user.delete()

    api_response = client.get(
        '/user/verify-user/{token}'.format(
            token=test_token4
        ),
        format='json'
    )
    assert api_response.status_code == 400
