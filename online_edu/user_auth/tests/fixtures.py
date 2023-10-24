import pytest

from user_auth.models import User


@pytest.fixture
def mock_send_email(monkeypatch):
    monkeypatch.setattr(
        'user_auth.views.send_verification_link_email',
        lambda user: print(
            'Sending email to {username}'.format(username=user.username)
        ),
        raising=True
    )


@pytest.fixture
def test_user():
    '''Create sample user for test'''
    sample_user = User.objects.create(username='someuser@somedomain.com')
    sample_user.set_password('somepassword')
    sample_user.save()
    return sample_user