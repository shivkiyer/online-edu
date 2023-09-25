import pytest
from .models import User

pytestmark = pytest.mark.django_db


def test_username_only_email():
    '''Test that the username can only be a valid email'''

    # Passing test with valid email
    user1 = User(username='someuser@domain.com')
    user1.set_password('somepasswordfortest')
    user1.save()
    users_in_db = User.objects.all().count()
    assert users_in_db == 1

    # Failing test with normal text instead of email
    with pytest.raises(Exception):
        user2 = User(username='someuser')
        user2.set_password('someotherpassword')
        user2.save()

    users_in_db = User.objects.all().count()
    assert users_in_db == 1
