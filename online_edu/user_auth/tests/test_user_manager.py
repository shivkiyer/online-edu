import pytest
import time

from .fixtures import test_user, \
    verification_token
from user_auth.models import User

pytestmark = pytest.mark.django_db


def test_get_user_by_id(test_user):
    '''Test the basic get_user_by_id query'''

    user1 = test_user(
        'someuser@domain.com',
        'somepassword',
        False
    )
    user2 = test_user(
        'anotheruser@domain.com',
        'anotherpassword',
        False
    )

    fetch_user = User.objects.get_user_by_id(1)
    assert fetch_user.username == 'someuser@domain.com'

    fetch_user = User.objects.get_user_by_id(2)
    assert fetch_user.username == 'anotheruser@domain.com'

    with pytest.raises(Exception) as e:
        fetch_user = User.objects.get_user_by_id(3)
    assert str(e.value) == 'User not found'


def test_get_user_by_token(test_user, verification_token):
    '''Test extracting user from JWT token'''

    user1 = test_user()

    token1 = verification_token(user1, 60)
    fetch_user = User.objects.get_user_by_token(str(token1))
    assert fetch_user.username == user1.username

    token2 = verification_token(user1, 1)
    time.sleep(2)
    with pytest.raises(Exception) as e:
        fetch_user = User.objects.get_user_by_token(token2)
    assert str(e.value) == 'Token is invalid or expired'


def test_get_user_by_email(test_user):
    '''Test extracting user from email'''

    user1 = test_user()

    fetch_user = User.objects.get_user_by_email(user1.username)
    assert fetch_user.username == user1.username

    with pytest.raises(Exception) as e:
        fetch_user = User.objects.get_user_by_email('anotheruser@domain.com')
    assert str(e.value) == 'User not found'


def test_active_user_by_token(test_user, verification_token):
    '''Test activating user from verification token'''

    user1 = test_user()

    token1 = verification_token(user1, 60)
    fetch_user = User.objects.activate_user_by_token(str(token1))
    assert fetch_user.is_active == True

    token2 = verification_token(user1, 1)
    time.sleep(2)
    with pytest.raises(Exception) as e:
        fetch_user = User.objects.activate_user_by_token(token2)
    assert str(e.value) == 'User could not be activated'
