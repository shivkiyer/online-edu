import logging
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import User
from .serializers import UserSerializer, \
    RegisterUserSerializer, \
    ChangePasswordSerializer
from .utils import send_verification_link_email, \
    send_password_reset_email
from common.error_definitions import DEFAULT_ERROR_RESPONSE, CustomAPIError

logger = logging.getLogger(__name__)


class RegisterUserView(CreateAPIView):
    '''Register a new user'''
    serializer_class = RegisterUserSerializer

    def post(self, *args, **kwargs):
        '''Create new user from API request'''
        user = RegisterUserSerializer(data=self.request.data)
        new_user = user.save()
        send_verification_link_email(new_user)
        logger.info('New user {} created'.format(new_user.id))
        return Response(user.data, status=status.HTTP_201_CREATED)


class VerifyUserView(APIView):
    '''Checks token received on clicking verification link'''

    def get(self, *args, **kwargs):
        verification_token = self.kwargs.get('token', None)
        if not verification_token:
            logger.critical(
                'No token passed for verifying registered user'
            )
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Broken link'
            )
        try:
            token_data = TokenRefreshSerializer(
                data={'refresh': verification_token}
            )
            token_data.is_valid()
        except:
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Link expired or faulty'
            )
        # Set the user to active
        new_user = User.objects.activate_user_by_token(
            verification_token)
        logger.info('User {} verified'.format(new_user.id))
        return Response(status=status.HTTP_200_OK)


class ResendVerificationEmailView(APIView):
    '''Resending verification email to user'''

    def post(self, *args, **kwargs):
        user_email = self.request.data.get('email', None)
        user_obj = User.objects.get_user_by_email(user_email)
        send_verification_link_email(user_obj)
        logger.info('Verification email resent to user {}'.format(
            user_obj.id))
        return Response(
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
            user_token = AccessToken.for_user(user_obj)
            logger.info('User {} logged in successfully'.format(
                user_obj.id
            )
            )
            return Response(
                data=str(user_token),
                status=status.HTTP_200_OK
            )
        else:
            logger.critical(
                'User {} not validated'.format(
                    self.request.data.get('username', None)
                )
            )
            raise CustomAPIError(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid username/password'
            )


class ResetPasswordView(APIView):
    '''Send password reset link to user email'''

    def post(self, *args, **kwargs):
        user_email = self.request.data.get('email', None)
        user_obj = User.objects.get_user_by_email(user_email)
        send_password_reset_email(user_obj)
        logger.info('Password reset email sent to user {}'.format(
            user_obj.id))
        return Response(
            status=status.HTTP_200_OK
        )


class ChangePasswordView(APIView):
    '''Change a user password'''

    serializer_class = ChangePasswordSerializer

    def post(self, *args, **kwargs):
        verification_token = self.kwargs.get('token', None)
        if not verification_token:
            logger.critical(
                'No token passed for changing password'
            )
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Broken link'
            )
        # Check for expired token
        try:
            token_data = TokenRefreshSerializer(
                data={'refresh': verification_token}
            )
            token_data.is_valid()
        except Exception as e:
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Link expired or faulty'
            )
        user_obj = User.objects.get_user_by_token(verification_token)
        user_form = ChangePasswordSerializer(
            user_obj,
            data=self.request.data
        )
        # Check for password match
        user_form.save()
        logger.info('Password changed for user {}'.format(
            user_obj.id))
        return Response(status=status.HTTP_200_OK)


class UserAuthentication(JWTAuthentication):
    '''Returns user from token in header'''

    def authenticate(
        self,
        request,
        check_admin=True,
        open_endpoint=False,
        *args,
        **kwargs
    ):
        error_msg = None
        try:
            user = super().authenticate(request, *args, **kwargs)
            if user is not None:
                if check_admin and not user[0].is_staff:
                    error_msg = 'Admin privileges required for this action'
                else:
                    request.user = user[0]
                    return user[0]
            else:
                request.user = None
        except Exception as e:
            raise CustomAPIError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Must be logged in for this action'
            )
        if not open_endpoint:
            if error_msg is None:
                error_msg = 'Invalid login or inactive account'
            raise CustomAPIError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_msg
            )
        else:
            return None
