from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication

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
            request.user = user[0]
            return super().create(request, *args, **kwargs)
        except:
            return Response(
                data='Must be logged in as administrator to create a course',
                status=status.HTTP_403_FORBIDDEN
            )
