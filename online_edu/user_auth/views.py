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
from common.error_definitions import DEFAULT_ERROR_RESPONSE
from common.error_handling import serializer_error_response
from .error_definitions import UserGenericException

logger = logging.getLogger(__name__)


class RegisterUserView(CreateAPIView):
    '''Register a new user'''
    serializer_class = RegisterUserSerializer

    def post(self, *args, **kwargs):
        '''Create new user from API request'''
        try:
            user = RegisterUserSerializer(data=self.request.data)
        except Exception as e:
            logger.critical(
                'Error in registering new user - {error}'.format(error=str(e))
            )
            return Response(
                data=DEFAULT_ERROR_RESPONSE,
                status=status.HTTP_400_BAD_REQUEST
            )
        new_user = None
        if user.is_valid():
            try:
                new_user = user.save()
                send_verification_link_email(new_user)
                logger.info('New user {} created'.format(new_user.username))
                return Response(user.data, status=status.HTTP_201_CREATED)
            except UserGenericException as e:
                logger.error(
                    'Error in registering new user {username} - {error}'.format(
                        username=user.data['username'],
                        error=str(e)
                    )
                )
                return Response(
                    data=str(e),
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                logger.critical(
                    'Error in registering new user - {error}'.format(
                        error=str(e)
                    )
                )
                return Response(
                    data=DEFAULT_ERROR_RESPONSE,
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return serializer_error_response(user, 'Could not register user')


class VerifyUserView(APIView):
    '''Checks token received on clicking verification link'''

    def get(self, *args, **kwargs):
        verification_token = self.kwargs.get('token', None)
        if not verification_token:
            logger.critical(
                'No token passed for verification registered user'
            )
            return Response(
                data='Broken link',
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            try:
                token_data = TokenRefreshSerializer(
                    data={'refresh': verification_token}
                )
                token_data.is_valid()
            except:
                return Response(
                    data='Link expired or faulty',
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Set the user to active
            new_user = User.objects.activate_user_by_token(
                verification_token)
            logger.info('User {} verified'.format(new_user.username))
            return Response(status=status.HTTP_200_OK)
        except UserGenericException as e:
            logger.error(
                'Error in verifying user - {}'.format(str(e))
            )
            return Response(
                data=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )
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
        user_id = self.kwargs.get('user_id', None)
        try:
            user_obj = User.objects.get_user_by_id(user_id)
            send_verification_link_email(user_obj)
            logger.info('Verification email resent to user {}'.format(
                user_obj.username))
            return Response(
                status=status.HTTP_200_OK
            )
        except UserGenericException as e:
            logger.error(
                'Error in resending verification email - {}'.format(str(e))
            )
            return Response(
                data=str(e),
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
                data=DEFAULT_ERROR_RESPONSE,
                status=status.HTTP_400_BAD_REQUEST
            )


class LoginUserView(APIView):
    '''Login user and return token'''
    serializer_class = UserSerializer

    def post(self, *args, **kwargs):
        try:
            user_obj = authenticate(
                username=self.request.data.get('username', None),
                password=self.request.data.get('password', None)
            )
        except UserGenericException as e:
            logger.error(
                'Error logging in user - {}'.format(str(e))
            )
            return Response(
                data=str(e),
                status=status.HTTP_401_UNAUTHORIZED
            )
        except:
            return Response(
                data=DEFAULT_ERROR_RESPONSE,
                status=status.HTTP_400_BAD_REQUEST
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
        user_id = self.kwargs.get('user_id', None)
        try:
            user_obj = User.objects.get_user_by_id(user_id)
            send_password_reset_email(user_obj)
            logger.info('Password reset email sent to user {}'.format(
                user_obj.username))
            return Response(
                status=status.HTTP_200_OK
            )
        except UserGenericException as e:
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
        except Exception as e:
            logger.error(
                'Password failed for user Id {user_id} - {error}'.format(
                    user_id=user_id,
                    error=str(e)
                )
            )
            return Response(
                data=DEFAULT_ERROR_RESPONSE,
                status=status.HTTP_400_BAD_REQUEST
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
            return Response(
                data='Broken link',
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            # Check for expired token
            try:
                token_data = TokenRefreshSerializer(
                    data={'refresh': verification_token}
                )
                token_data.is_valid()
            except Exception as e:
                return Response(
                    data='Link expired or faulty',
                    status=status.HTTP_400_BAD_REQUEST
                )
            user_obj = User.objects.get_user_by_token(verification_token)
            user_form = ChangePasswordSerializer(
                user_obj,
                data=self.request.data
            )
            # Check for password match
            if not user_form.is_valid():
                return serializer_error_response(
                    user_form,
                    'Could not change user password'
                )
            else:
                user_form.save()
                logger.info('Password changed for user {}'.format(
                    user_obj.username))
                return Response(status=status.HTTP_200_OK)
        except UserGenericException as e:
            logger.error(
                'Change password failed - {error}'.format(error=str(e))
            )
            return Response(
                data=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(
                'Password change failed for user - {error}'.format(
                    error=str(e)
                )
            )
            return Response(
                data=DEFAULT_ERROR_RESPONSE,
                status=status.HTTP_400_BAD_REQUEST
            )


class UserAuthentication(JWTAuthentication):
    '''Returns user from token in header'''

    def authenticate(self, request, check_admin=True, *args, **kwargs):
        user = super().authenticate(request, *args, **kwargs)
        if user is not None:
            if check_admin and not user[0].is_staff:
                return None
            request.user = user[0]
            return user[0]
