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
    '''
    Register a new user

    Attributes
    ----------------
    serializer_class : RegisterUserSerializer

    Methods
    ----------------
    post(*args, **kwargs):
        Register a new user and return new user data
    '''
    serializer_class = RegisterUserSerializer

    def post(self, *args, **kwargs):
        '''
        Create new user from API request

        Raises
        ---------------
        400 error
            If username is missing
            If username is not a valid email
            If password is missing
            If confirm_password is missing
            If password and confirm_password are not matching

        Returns
        ---------------
        Response with user data
        '''
        user = RegisterUserSerializer(data=self.request.data)
        new_user = user.save()
        send_verification_link_email(new_user)
        logger.info(
            f'New user {new_user.id} created'
        )
        return Response(user.data, status=status.HTTP_201_CREATED)


class VerifyUserView(APIView):
    '''
    Checks token received on clicking verification link

    Methods
    --------------------
    get(*args, **kwargs):
        Processes verification link click
    '''

    def get(self, *args, **kwargs):
        '''
        Activate user from verification link

        Raises
        -----------------
        400 error
            Invalid link if token is missing
            Link expired or faulty is token is expired or tampered
        '''
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
        logger.info(
            f'User {new_user.id} verified'
        )
        return Response(status=status.HTTP_200_OK)


class ResendVerificationEmailView(APIView):
    '''
    Resending verification email to user

    Methods
    --------------
    post(*args, **kwargs):
        Resend verification link to provided email
    '''

    def post(self, *args, **kwargs):
        '''
        Resend verification link to provided email

        Raises
        ----------------
        404 error
            User not found from email
        '''
        user_email = self.request.data.get('email', None)
        user_obj = User.objects.get_user_by_email(user_email)
        send_verification_link_email(user_obj)
        logger.info(
            f'Verification email resent to user {user_obj.id}'
        )
        return Response(
            status=status.HTTP_200_OK
        )


class LoginUserView(APIView):
    '''
    Login user and return token

    Methods
    ----------------
    post(*args, **kwargs):
        Login a user and return JWT
    '''
    serializer_class = UserSerializer

    def post(self, *args, **kwargs):
        '''
        Log a user in with email and password

        Raises
        --------------
        401 error
            Invalid username/password if login fails
        '''
        user_obj = authenticate(
            username=self.request.data.get('username', None),
            password=self.request.data.get('password', None)
        )
        if user_obj is not None:
            user_token = AccessToken.for_user(user_obj)
            logger.info(
                f'User {user_obj.id} logged in successfully'
            )
            return Response(
                data=str(user_token),
                status=status.HTTP_200_OK
            )
        else:
            logger.critical(
                f'User {self.request.data.get("username", None)} not validated'
            )
            raise CustomAPIError(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid username/password'
            )


class ResetPasswordView(APIView):
    '''
    Send password reset link to user email

    Methods
    ---------------
    post(*args, **kwargs):
        Send a password reset link to provided email
    '''

    def post(self, *args, **kwargs):
        '''
        Send a password reset link to provided email

        Raises
        --------------
        404 error
            If user not found from email
        '''
        user_email = self.request.data.get('email', None)
        user_obj = User.objects.get_user_by_email(user_email)
        send_password_reset_email(user_obj)
        logger.info(
            f'Password reset email sent to user {user_obj.id}'
        )
        return Response(
            status=status.HTTP_200_OK
        )


class ChangePasswordView(APIView):
    '''
    Change a user password

    Methods
    -----------------
    post(*args, **kwargs):
        Update a user password
    '''

    serializer_class = ChangePasswordSerializer

    def post(self, *args, **kwargs):
        '''
        Update a user password

        Raises
        ----------------
        400 error
            If request does not contain JWT or if JWT expired
        404 error
            If user cannot be found
        '''
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
        logger.info(
            f'Password changed for user {user_obj.id}'
        )
        return Response(status=status.HTTP_200_OK)


class UserAuthentication(JWTAuthentication):
    '''
    Returns user from token in header

    Methods
    --------------------
    authenticate:
        Extract JWT from request header and return user model instance
    '''

    def authenticate(
        self,
        request,
        check_admin=True,
        open_endpoint=False,
        *args,
        **kwargs
    ):
        '''
        Extract JWT from request header and return user model instance.
        User model instance is also inserted into request object.

        Parameters
        ---------------
        request : Request
        check_admin : boolean
            If the authentication should enforce admin only credentials.
            Default is True
        open_endpoint : boolean
            If the endpoint requesting does not need authentication.
            Default is False.

        Raises
        ---------------
        403 error
            If no token in header
            If admin is required by token is not of admin user
        '''
        error_msg = None
        request.user = None
        try:
            user = super().authenticate(request, *args, **kwargs)
            if user is not None:
                request.user = user[0]
                if check_admin and not user[0].is_staff:
                    error_msg = 'Admin privileges required for this action'
                else:
                    return user[0]
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
