import pytest


@pytest.fixture
def mock_send_email(monkeypatch):
    monkeypatch.setattr(
        'user_auth.views.send_verification_link_email',
        lambda user: print(
            'Sending email to {username}'.format(username=user.username)
        ),
        raising=True
    )
