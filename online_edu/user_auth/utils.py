from django.conf import settings
from django.core.mail import send_mail


def send_verification_link_email(username):
    '''Send an email to newly registered used with verification link'''

    message_body = (
        "Hello,\n"
        "Thank you for registering with Online Edu!\n"
        "\n"
        "You are not yet ready to use your account. Before you can login to the website, please verify your email by clicking on this link:\n"
        "http://www.google.com \n"
        "\n"
        "Please click on this link within 15 minutes of receiving this email.\n"
        "\n"
        "Thank you,\n"
        "Online Edu"
    )

    send_mail(
        subject='Verification link',
        message=message_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[username]
    )
