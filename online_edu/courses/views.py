from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import InvalidToken

from user_auth.models import User
from .models import Course
from .serializers import CourseSerializer


class CourseCreateView(CreateAPIView, JWTAuthentication):
    '''Create a course with logged-in user as instructor'''

    serializer_class = CourseSerializer
    user_model = User

    def perform_create(self, serializer):
        course = serializer.save()
        course.add_instructor(self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            user = self.authenticate(request)
            if user is not None and user[0].is_staff:
                request.user = user[0]
                return super().create(request, *args, **kwargs)
            else:
                return Response(
                    data='Must be logged in as administrator to create a course',
                    status=status.HTTP_403_FORBIDDEN
                )
        except ValidationError as e:
            try:
                err_message = [e.detail[err][0] for err in e.detail][0]
            except:
                err_message = 'Course could not be created'
            return Response(
                data=err_message,
                status=status.HTTP_400_BAD_REQUEST
            )
        except InvalidToken as e:
            try:
                error_message = e.detail['messages'][0]['message']
            except:
                error_message = 'Course could not be created'
            return Response(
                data=error_message,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                data=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )
