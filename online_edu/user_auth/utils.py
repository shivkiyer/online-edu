from datetime import timedelta
import logging
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from .error_definitions import UserGenericException

logger = logging.getLogger(__name__)


def send_verification_link_email(user):
    '''Send an email to newly registered used with verification link'''
    if not user:
        raise UserGenericException('No user to send email to')
    if user.is_active:
        raise UserGenericException('User already activated')

    verification_token = RefreshToken.for_user(user)
    message_body = (
        "Hello,\n"
        "Thank you for registering with Online Edu!\n"
        "\n"
        "You are not yet ready to use your account. Before you can login to the website, please verify your email by clicking on this link:\n"
        "{base_url}{token_url} \n"
        "\n"
        "Please click on this link within {time_limit} minutes of receiving this email.\n"
        "\n"
        "Thank you,\n"
        "Online Edu"
    ).format(
        base_url=settings.BASE_URL,
        token_url=reverse(
            'user_auth:verify-user',
            args=[verification_token]
        ),
        time_limit=settings.EMAIL_VERIFICATION_TIMELIMIT
    )

    send_mail(
        subject='Verification link',
        message=message_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.username]
    )
    logger.info('Sent verification email to {}'.format(user.username))
    return


def send_password_reset_email(user):
    '''Send a password reset email to an active user'''
    if not user or not user.is_active:
        raise UserGenericException('No user to send email to')

    verification_token = RefreshToken.for_user(user)
    message_body = (
        "Hello,\n"
        "Here is your password reset link:\n"
        "{base_url}{token_url} \n"
        "\n"
        "Please click on this link within {time_limit} minutes of receiving this email.\n"
        "\n"
        "Thank you,\n"
        "Online Edu"
    ).format(
        base_url=settings.BASE_URL,
        token_url=reverse(
            'user_auth:change-password',
            args=[verification_token]
        ),
        time_limit=settings.EMAIL_VERIFICATION_TIMELIMIT
    )

    send_mail(
        subject='Password reset link',
        message=message_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.username]
    )
    logger.info('Sent password reset email to {}'.format(user.username))
    return
