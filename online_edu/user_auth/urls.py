from django.urls import path

from .views import RegisterUserView, \
    VerifyUserView, \
    ResendVerificationEmailView, \
    LoginUserView, \
    ResetPasswordView, \
    ChangePasswordView

app_name = 'user_auth'
urlpatterns = [
    path('register-user', RegisterUserView.as_view(), name='register-user'),
    path('verify-user/<str:token>', VerifyUserView.as_view(), name='verify-user'),
    path(
        'resend-verification/<int:user_id>',
        ResendVerificationEmailView.as_view(),
        name='resend-verificaion-email'
    ),
    path('login', LoginUserView.as_view(), name='login-user'),
    path(
        'reset-password/<int:user_id>',
        ResetPasswordView.as_view(),
        name='reset-password'
    ),
    path(
        'change-password/<str:token>',
        ChangePasswordView.as_view(),
        name='change-password'
    ),
]
