from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import RegisterUserSerializer
from .utils import send_verification_link_email


class RegisterUserView(CreateAPIView):
    '''Register a new user'''
    serializer_class = RegisterUserSerializer

    def post(self, *args, **kwargs):
        '''Create new user from API request'''
        user = RegisterUserSerializer(data=self.request.data)
        if user.is_valid():
            try:
                user.save()
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
        send_verification_link_email(username=user.data['username'])
        return Response(user.data, status=status.HTTP_201_CREATED)
