import logging
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken

from .models import User
from .serializers import UserSerializer, \
    RegisterUserSerializer, \
    ChangePasswordSerializer
from .utils import send_verification_link_email, \
    send_password_reset_email, \
    serializer_error_response, \
    token_error_response

logger = logging.getLogger(__name__)


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
                send_verification_link_email(new_user)
                logger.info('New user {} created'.format(new_user.username))
                return Response(user.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(
                    'Error in registering new user {username} - {error}'.format(
                        username=user.data['username'],
                        error=str(e)
                    )
                )
                return Response(
                    data=e,
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return serializer_error_response(user)


class VerifyUserView(APIView):
    '''Checks token received on clicking verification link'''

    def get(self, *args, **kwargs):
        verification_token = self.kwargs['token']
        if not verification_token:
            logger.critical(
                'No token passed for verification registered user'
            )
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
                new_user = User.objects.activate_user_by_token(
                    verification_token)
                logger.info('User {} verified'.format(new_user.username))
                return Response(status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(
                'Error in verifying user - {}'.format(str(e))
            )
            return Response(
                data=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )


class ResendVerificationEmailView(APIView):
    '''Resending verification email to user'''

    def get(self, *args, **kwargs):
        user_id = self.kwargs['user_id']
        try:
            user_obj = User.objects.get(id=user_id)
            send_verification_link_email(user_obj)
            logger.info('Verification email resent to user {}'.format(
                user_obj.username))
            return Response(
                status=status.HTTP_200_OK
            )
        except ObjectDoesNotExist:
            logger.critical(
                'User with non-existant Id {} tried to get verification email'.format(
                    user_id
                )
            )
            return Response(
                data='User not found',
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(
                'Resending verification failed for user Id {user_id} - {error}'.format(
                    user_id=user_id,
                    error=str(e)
                )
            )
            return Response(
                data=str(e),
                status=status.HTTP_400_BAD_REQUEST
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
                user_obj.username
            )
            )
            return Response(
                data=str(user_token),
                status=status.HTTP_200_OK
            )
        else:
            logger.error(
                'User {} not validated'.format(
                    self.request.data.get('username', None)
                )
            )
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
            logger.info('Password reset email sent to user {}'.format(
                user_obj.username))
            return Response(
                status=status.HTTP_200_OK
            )
        except ObjectDoesNotExist:
            logger.critical(
                'User with non-existant Id {} tried to reset password'.format(
                    user_id
                )
            )
            return Response(
                data='User not found',
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(
                'Password failed for user Id {user_id} - {error}'.format(
                    user_id=user_id,
                    error=str(e)
                )
            )
            return Response(
                data=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )


class ChangePasswordView(APIView):
    '''Change a user password'''

    serializer_class = ChangePasswordSerializer

    def post(self, *args, **kwargs):
        verification_token = self.kwargs['token']
        if not verification_token:
            logger.critical(
                'No token passed for changing password'
            )
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
                    logger.info('Password changed for user {}'.format(
                        user_obj.username))
                    return Response(status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(
                'Password change failed for user - {error}'.format(
                    error=str(e)
                )
            )
            return Response(
                data=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )
