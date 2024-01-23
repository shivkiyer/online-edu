import pytest

from .fixtures import test_user, mock_send_mail
from user_auth.utils import send_verification_link_email, \
    send_password_reset_email

pytestmark = pytest.mark.django_db


def test_send_verification_link_email(test_user, mock_send_mail):
    '''Test emailing verification link'''

    user1 = test_user
    user1.is_active = False
    user1.save()

    with pytest.raises(Exception) as e:
        send_verification_link_email(None)
    assert str(e.value) == 'No user to send email to'

    # send_mail method with throw error when called
    mock_send_mail(True)

    with pytest.raises(Exception) as e:
        send_verification_link_email(user1)
    assert str(e.value) == 'mock_send_email called'

    # send_mail will only print a message
    mock_send_mail(False)

    user1.is_active = True
    user1.save()
    with pytest.raises(Exception) as e:
        send_verification_link_email(user1)
    assert str(e.value) == 'User already activated'


def test_send_password_reset_email(test_user, mock_send_mail):
    '''Testing send_password_reset_email'''

    user1 = test_user

    with pytest.raises(Exception) as e:
        send_password_reset_email(None)
    assert str(e.value) == 'No user to send email to'

    user1.is_active = False
    user1.save()

    with pytest.raises(Exception) as e:
        send_password_reset_email(user1)
    assert str(e.value) == 'No user to send email to'

    # send_mail will throw an error when called
    mock_send_mail(True)

    user1.is_active = True
    user1.save()

    with pytest.raises(Exception) as e:
        send_password_reset_email(user1)
    assert str(e.value) == 'mock_send_email called'
