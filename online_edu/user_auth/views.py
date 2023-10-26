from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSerializer, \
    RegisterUserSerializer, \
    ChangePasswordSerializer
from .utils import send_verification_link_email, \
    send_password_reset_email, \
    serializer_error_response, \
    token_error_response


class RegisterUserView(CreateAPIView):
    '''Register a new user'''
    serializer_class = RegisterUserSerializer

    def post(self, *args, **kwargs):
        '''Create new user from API request'''
        user = RegisterUserSerializer(data=self.request.data)
        new_user = None
        if user.is_valid():
            try:
                new_user = user.save()
            except Exception as e:
                return Response(
                    data=e,
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return serializer_error_response(user)
        send_verification_link_email(new_user)
        return Response(user.data, status=status.HTTP_201_CREATED)


class VerifyUserView(APIView):
    '''Checks token received on clicking verification link'''

    def get(self, *args, **kwargs):
        verification_token = self.kwargs['token']
        if not verification_token:
            return Response(
                data='Missing token',
                status=status.HTTP_400_BAD_REQUEST
            )
        token_data = TokenRefreshSerializer(
            data={'refresh': verification_token}
        )
        try:
            if not token_data.is_valid():
                return token_error_response(token_data)
            else:
                # Set the user to active
                User.objects.activate_user_by_token(verification_token)
        except Exception as e:
            return Response(
                data=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_200_OK)


class ResendVerificationEmailView(APIView):
    '''Resending verification email to user'''

    def get(self, *args, **kwargs):
        user_id = self.kwargs['user_id']
        try:
            user_obj = User.objects.get(id=user_id)
        except Exception as e:
            return Response(
                data=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )
        send_verification_link_email(user_obj)
        user_data = UserSerializer(user_obj)
        return Response(
            data=user_data.data,
            status=status.HTTP_200_OK
        )


class LoginUserView(APIView):
    '''Login user and return token'''
    serializer_class = UserSerializer

    def post(self, *args, **kwargs):
        user_obj = authenticate(
            username=self.request.data.get('username', None),
            password=self.request.data.get('password', None)
        )
        if user_obj is not None:
            user_token = RefreshToken.for_user(user_obj)
            return Response(
                data=str(user_token),
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                data='Invalid username/password',
                status=status.HTTP_401_UNAUTHORIZED
            )


class ResetPasswordView(APIView):
    '''Send password reset link to user email'''

    def get(self, *args, **kwargs):
        user_id = self.kwargs['user_id']
        try:
            user_obj = User.objects.get(id=user_id)
            send_password_reset_email(user_obj)
        except Exception as e:
            return Response(
                data=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            status=status.HTTP_200_OK
        )


class ChangePasswordView(APIView):
    '''Change a user password'''

    serializer_class = ChangePasswordSerializer

    def post(self, *args, **kwargs):
        verification_token = self.kwargs['token']
        if not verification_token:
            return Response(
                data='Missing token',
                status=status.HTTP_400_BAD_REQUEST
            )
        token_data = TokenRefreshSerializer(
            data={'refresh': verification_token}
        )
        try:
            # Check for expired token
            if not token_data.is_valid():
                return token_error_response(token_data)
            else:
                user_obj = User.objects.get_user_by_token(verification_token)
                user_form = ChangePasswordSerializer(
                    user_obj,
                    data=self.request.data
                )
                # Check for password match
                if not user_form.is_valid():
                    return serializer_error_response(user_form)
                else:
                    user_form.save()
        except Exception as e:
            return Response(
                data=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_200_OK)
