from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from .models import Course
from .serializers import CourseSerializer


class CourseCreateView(CreateAPIView):
    '''Create a course with logged-in user as instructor'''

    serializer_class = CourseSerializer
