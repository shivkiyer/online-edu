from django.urls import path

from .views import RegisterUserView, VerifyUserView

app_name = 'user_auth'
urlpatterns = [
    path('register-user', RegisterUserView.as_view(), name='register-user'),
    path('verify-user/<str:token>', VerifyUserView.as_view(), name='verify-user'),
]
