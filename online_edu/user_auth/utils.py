from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status


def send_verification_link_email(user):
    '''Send an email to newly registered used with verification link'''
    if not user:
        raise ValidationError('No user to send email to')
    if user.is_active:
        raise ValidationError('User already activated')

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
    return


def send_password_reset_email(user):
    '''Send a password reset email to an active user'''
    if not user or not user.is_active:
        raise ValidationError('No user to send email to')

    verification_token = RefreshToken.for_user(user)
    verification_token.set_exp(
        from_time=verification_token.current_time,
        lifetime=timedelta(minutes=settings.EMAIL_VERIFICATION_TIMELIMIT)
    )
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
    return


def token_error_response(token):
    '''Return 400 HTTP error if JWT has errors'''
    error_list = [token.errors[e][0].title()
                  for e in token.errors]
    return Response(
        data=error_list[0],
        status=status.HTTP_400_BAD_REQUEST
    )


def serializer_error_response(serializer):
    '''Return 400 HTTP error if serializer has errors'''
    error_list = [serializer.errors[e][0].title()
                  for e in serializer.errors]
    return Response(
        data=error_list[0],
        status=status.HTTP_400_BAD_REQUEST
    )
