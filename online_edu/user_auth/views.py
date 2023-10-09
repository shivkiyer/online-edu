from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import RegisterUserSerializer
from .utils import send_verification_link_email


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
            error_list = [user.errors[e][0].title() for e in user.errors]
            return Response(
                data=error_list[0],
                status=status.HTTP_400_BAD_REQUEST
            )
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
                error_list = [token_data.errors[e][0].title()
                              for e in token_data.errors]
                return Response(
                    data=error_list[0],
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                # Set the user to active
                user_data = RefreshToken(verification_token)
                user_obj = User.objects.get(id=int(user_data['user_id']))
                user_obj.is_active = True
                user_obj.save()
        except Exception as e:
            return Response(
                data=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_200_OK)
