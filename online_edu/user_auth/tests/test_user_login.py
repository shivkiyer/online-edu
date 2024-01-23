import pytest
from rest_framework.test import APIClient

from .fixtures import test_user

pytestmark = pytest.mark.django_db


def test_user_login_endpoint(test_user):
    '''Test the endpoint of logging user in'''

    client = APIClient()

    user1 = test_user()

    # Successful login
    api_response = client.post(
        '/api/user/login',
        {
            'username': 'someuser@somedomain.com',
            'password': 'somepassword'
        },
        format='json'
    )
    assert api_response.status_code == 200

    # Missing username and/or password
    api_response = client.post(
        '/api/user/login',
        {
            'username': 'someuser@somedomain.com',
        },
        format='json'
    )
    assert api_response.data == 'Invalid username/password'
    assert api_response.status_code == 401

    api_response = client.post(
        '/api/user/login',
        {
            'password': 'somepassword'
        },
        format='json'
    )
    assert api_response.data == 'Invalid username/password'
    assert api_response.status_code == 401

    api_response = client.post(
        '/api/user/login',
        {},
        format='json'
    )
    assert api_response.data == 'Invalid username/password'
    assert api_response.status_code == 401

    # Wrong password
    api_response = client.post(
        '/api/user/login',
        {
            'username': 'someuser@somedomain.com',
            'password': 'somepassword1'
        },
        format='json'
    )
    assert api_response.data == 'Invalid username/password'
    assert api_response.status_code == 401

    # Wrong username
    api_response = client.post(
        '/api/user/login',
        {
            'username': 'someuser@somedomain.com1',
            'password': 'somepassword'
        },
        format='json'
    )
    assert api_response.data == 'Invalid username/password'
    assert api_response.status_code == 401

    # Wrong username and password
    api_response = client.post(
        '/api/user/login',
        {
            'username': 'someuser@somedomain.com1',
            'password': 'somepassword1'
        },
        format='json'
    )
    assert api_response.data == 'Invalid username/password'
    assert api_response.status_code == 401
