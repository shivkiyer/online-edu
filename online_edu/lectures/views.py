from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, \
    ListModelMixin, \
    RetrieveModelMixin

from user_auth.models import User
from user_auth.views import UserAuthentication
from courses.models import Course
from common.error_definitions import CustomAPIError
from .models import Lecture
from .serializers import LectureSerializer


class LectureBaseView(GenericAPIView, UserAuthentication):
    '''Basic lecture view'''

    serializer_class = LectureSerializer
    user_model = User
    lookup_field = 'id'
    course = None

    def init_lecture(self, login_required=True):
        '''
        Initialize lecture view
            - fetch course object
            - authenticate user
        '''
        course_slug = self.kwargs.get('slug', None)
        self.course = Course.objects.get_course_by_slug(course_slug)
        if login_required:
            self.authenticate(self.request)

    def get_queryset(self):
        self.init_lecture(login_required=False)
        return Lecture.objects.filter(
            course=self.course
        )

    def get_object(self):
        self.init_lecture()
        try:
            return super().get_object()
        except:
            raise CustomAPIError(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Lecture not found'
            )


class LectureView(
    LectureBaseView,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin
):
    '''Basic lecture view'''

    def get(self, request, *args, **kwargs):
        if self.kwargs.get('id', None) is None:
            return self.list(request, *args, **kwargs)
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.init_lecture()
        serializer = LectureSerializer(data=request.data)
        serializer.save(
            user=self.request.user,
            course=self.course
        )
        return Response(serializer.data)
