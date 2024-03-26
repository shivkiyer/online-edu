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
    '''
    Base view for a course based on course URL

    Attributes
    -------------
    serializer_class : class
        CourseSerializer class
    user_model : class
        User class
    lookup_field : str
        The field in URL used to look up model instance

    Methods
    -------------
    get_queryset() : Base method for course list view
    get_object() : Returns course model instance
    '''

    serializer_class = CourseSerializer
    user_model = User
    lookup_field = 'slug'

    def get_queryset(self, *args, **kwargs):
        '''
        Return list of courses.
        If requesting user is admin, all courses are returned.
        If requesting user is non-admin, only published courses
        not archived are returned.
        '''
        if self.request.user is not None and self.request.user.is_staff:
            return Course.objects.all()
        return Course.objects.fetch_courses()

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
    '''
    CRUD operations on Course

    Methods
    -------------
    perform_create(serializer) : Saves serializer data to create new course
    perform_update(serializer) : Updates course with serializer data
    post(request) : Handles POST requests
    get(request) : Handles GET requests (list and detail)
    patch(request) : Handles PATCH requests (partial update of course)
    '''

    def perform_create(self, serializer):
        '''
        Create a new course with authenticated user as instructor

        Parameters
        --------------
        serializer : Serializer instance
        '''
        course = serializer.save(user=self.request.user)
        logger.info(
            f'Creating course {course.id} by user {self.request.user.id}'
        )

    def perform_update(self, serializer):
        '''
        Update a course by an authenticated instructor

        Parameters
        --------------
        serializer : Serializer instance
        '''
        course = serializer.save(user=self.request.user)
        logger.info(
            f'Updating course {course.id} by user {self.request.user.id}'
        )

    def post(self, request, *args, **kwargs):
        '''
        Create a new course - POST request

        Parameters
        --------------
        request - dict

        Raises
        --------------
        400 error
            Course title missing or not unique
            Course price missing for non-free course
        403 error
            If course created by non-admin user

        Returns
        --------------
        201 response with course data
        '''
        self.authenticate(request)
        serializer = self.get_serializer(data=request.data)
        self.perform_create(serializer)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def get(self, request, *args, **kwargs):
        '''
        Fetch all courses or specific course by slug

        Parameters
        -------------
        request - dict

        Raises
        -------------
        404 error
            If slug is for a course that does not exist or
            if non-admin user is accessing unpublished course

        Returns
        -------------
        200 response with course list or course data
        '''
        slug = self.kwargs.get('slug', None)
        self.authenticate(request, open_endpoint=True)
        user_id = None
        if self.request.user is not None:
            user_id = self.request.user.id
        if slug:
            logger.info(
                f'Course with slug {slug} fetched by user {user_id}'
            )
            return self.retrieve(request, *args, *kwargs)
        else:
            logger.info(
                f'Course list fetched by user {user_id}'
            )
            return self.list(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        '''
        Update a course by an authenticated instructor

        Parameters
        -------------
        request - dict

        Raises
        -------------
        400 error
            If new course title is not unique
        403 error
            If user updating course is not an instructor

        Returns
        -------------
        200 error response with course data
        '''
        self.authenticate(request)
        return self.partial_update(request, *args, **kwargs)
