import pytest
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from user_auth.models import User


@pytest.fixture
def mock_send_mail(monkeypatch):

    def _email_generator(throw_error=False):

        def _email_fn(*args, **kwargs):
            print('Sending email')
            if throw_error:
                raise Exception('mock_send_email called')

        monkeypatch.setattr(
            'user_auth.utils.send_mail',
            _email_fn,
            raising=True
        )

    return _email_generator


@pytest.fixture
def mock_send_verification_email(monkeypatch):
    monkeypatch.setattr(
        'user_auth.views.send_verification_link_email',
        lambda user: print(
            f'Sending verification email to {user.username}'
        ),
        raising=True
    )


@pytest.fixture
def mock_send_password_reset_email(monkeypatch):
    monkeypatch.setattr(
        'user_auth.views.send_password_reset_email',
        lambda user: print(
            f'Sending password reset email to {user.username}'
        ),
        raising=True
    )


@pytest.fixture
def test_user():
    '''User with username, password and admin status as arguments'''

    def _user_gen(username=None, password=None, is_staff=False):
        if username is None:
            username = 'someuser@somedomain.com'
        if password is None:
            password = 'somepassword'
        sample_user = User.objects.create(username=username, is_staff=is_staff)
        sample_user.set_password(password)
        sample_user.save()
        return sample_user

    return _user_gen


@pytest.fixture
def verification_token(test_user):
    '''Creating a verification token with JWT'''

    def _create_token(user=None, exp_time=60):
        '''Token with variable expiry time'''
        if user is None:
            user = test_user()
        verification_token = RefreshToken.for_user(user)
        verification_token.set_exp(
            from_time=verification_token.current_time,
            lifetime=timedelta(seconds=exp_time)
        )
        return verification_token

    return _create_token


@pytest.fixture
def access_token():
    '''Create an access token with JWT'''

    def _create_token(user, exp_time):
        '''Token with variable expiry time for any user'''
        access_token = AccessToken.for_user(user)
        access_token.set_exp(
            from_time=access_token.current_time,
            lifetime=timedelta(seconds=exp_time)
        )
        return access_token

    return _create_token
