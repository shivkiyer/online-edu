from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken


def send_verification_link_email(user):
    '''Send an email to newly registered used with verification link'''

    if not user:
        raise ValidationError('No user to send email to')

    verification_token = RefreshToken.for_user(user)
    verification_token.set_exp(
        from_time=verification_token.current_time,
        lifetime=timedelta(minutes=settings.EMAIL_VERIFICATION_TIMELIMIT)
    )
    message_body = (
        "Hello,\n"
        "Thank you for registering with Online Edu!\n"
        "\n"
        "You are not yet ready to use your account. Before you can login to the website, please verify your email by clicking on this link:\n"
        "{base_url}{token_url} \n"
        "\n"
        "Please click on this link within 15 minutes of receiving this email.\n"
        "\n"
        "Thank you,\n"
        "Online Edu"
    ).format(
        base_url=settings.BASE_URL,
        token_url=reverse(
            'user_auth:verify-user',
            args=[verification_token]
        )
    )

    send_mail(
        subject='Verification link',
        message=message_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.username]
    )
    return
