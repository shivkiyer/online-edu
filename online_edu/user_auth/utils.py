from datetime import timedelta
import logging
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from common.error_definitions import CustomAPIError

logger = logging.getLogger(__name__)


def send_verification_link_email(user):
    '''
    Send an email to newly registered used with verification link

    Parameters
    -------------
    user : User model instance

    Raises
    -------------
    400 error
        If user is missing
        If user is already activated
    '''
    if not user:
        raise CustomAPIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No user to send email to'
        )
    if user.is_active:
        raise CustomAPIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User already activated'
        )

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
    '''
    Send a password reset email to an active user

    Parameters
    -------------
    user : User model instance

    Raises
    -------------
    400 error
        If user is not activated
    '''
    if not user or not user.is_active:
        raise CustomAPIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No user to send email to'
        )

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
    logger.info(
        f'Sent password reset email to {user.username}'
    )
    return
