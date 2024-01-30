import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, \
    ListModelMixin, \
    RetrieveModelMixin, \
    UpdateModelMixin

from user_auth.models import User
from user_auth.views import UserAuthentication
from .models import Course
from .serializers import CourseSerializer
from common.error_definitions import DEFAULT_ERROR_RESPONSE, \
    CustomAPIError

logger = logging.getLogger(__name__)


class CourseBaseView(GenericAPIView, UserAuthentication):
    '''Base view for a course based on course URL'''

    serializer_class = CourseSerializer
    user_model = User
    lookup_field = 'slug'

    def get_object(self):
        '''Return 404 if course not found from slug'''
        try:
            return super().get_object()
        except:
            raise CustomAPIError(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Course not found from URL'
            )


class CourseView(
    CourseBaseView,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin
):
    '''CRUD operations on Course'''

    def get_queryset(self, *args, **kwargs):
        '''Return courses not in draft mode'''
        if self.request.user is not None and self.request.user.is_staff:
            return Course.objects.all()
        return Course.objects.fetch_courses()

    def perform_create(self, serializer):
        '''Create a new course with authenticated user as instructor'''
        course = serializer.save(user=self.request.user)
        logger.info(
            'Creating course {course} by user {user}'.format(
                course=course.id,
                user=self.request.user.id
            )
        )

    def perform_update(self, serializer):
        '''Update a course by an authenticated instructor'''
        course = serializer.save(user=self.request.user)
        logger.info(
            'Updating course {course} by user {user}'.format(
                course=course.id,
                user=self.request.user.id
            )
        )

    def post(self, request, *args, **kwargs):
        '''Create a new course - POST request'''
        self.authenticate(request)
        serializer = self.get_serializer(data=request.data)
        self.perform_create(serializer)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def get(self, request, *args, **kwargs):
        '''Fetch all courses or specific course by slug'''
        slug = self.kwargs.get('slug', None)
        self.authenticate(request, open_endpoint=True)
        if slug:
            return self.retrieve(request, *args, *kwargs)
        else:
            return self.list(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        '''Update a course by an authenticated instructor'''
        self.authenticate(request)
        return self.partial_update(request, *args, **kwargs)
