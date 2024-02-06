from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, \
    ListModelMixin, \
    RetrieveModelMixin, \
    UpdateModelMixin, \
    DestroyModelMixin

from user_auth.models import User
from user_auth.views import UserAuthentication
from courses.models import Course
from common.error_definitions import CustomAPIError
from registration.models import CourseStudentRegistration
from .models import Lecture
from .serializers import LectureSerializer


class LectureBaseView(GenericAPIView, UserAuthentication):
    '''Basic lecture view'''

    serializer_class = LectureSerializer
    user_model = User
    lookup_field = 'id'
    course = None

    def init_lecture(self, admin_only=True):
        '''
        Initialize lecture view
            - fetch course object
        '''
        course_slug = self.kwargs.get('slug', None)
        self.course = Course.objects.get_course_by_slug(
            course_slug,
            admin_only=admin_only
        )

    def check_lecture_permissions(self, request):
        if request.user is None:
            raise CustomAPIError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Must be logged in to access a lecture'
            )
        if not request.user.is_staff and not CourseStudentRegistration.objects.is_student_registered(
            user=request.user,
            course=self.course
        ):
            raise CustomAPIError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Must register for the course to access a lecture'
            )

    def get_queryset(self):
        return Lecture.objects.filter(
            course=self.course
        )

    def get_object(self):
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
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin
):
    '''Basic lecture view'''

    def perform_update(self, serializer):
        serializer.save(
            user=self.request.user,
            course=self.course
        )

    def get(self, request, *args, **kwargs):
        try:
            self.authenticate(request, check_admin=False)
        except Exception as e:
            pass
        if self.request.user is not None and self.request.user.is_staff:
            self.init_lecture()
        else:
            self.init_lecture(admin_only=False)
        if self.kwargs.get('id', None) is None:
            return self.list(request, *args, **kwargs)
        self.check_lecture_permissions(request)
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.authenticate(self.request)
        self.init_lecture()
        serializer = LectureSerializer(data=request.data)
        serializer.save(
            user=self.request.user,
            course=self.course
        )
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        self.authenticate(self.request)
        self.init_lecture()
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.authenticate(self.request)
        self.init_lecture()
        if not self.course.check_user_is_instructor(request.user):
            raise CustomAPIError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Only an instructor can delete lectures'
            )
        return self.destroy(request, *args, **kwargs)
