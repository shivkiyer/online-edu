import logging
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

logger = logging.getLogger(__name__)


class LectureBaseView(GenericAPIView, UserAuthentication):
    '''
    Basic lecture view

    Attributes
    ---------------
    serializer_class : class
        LectureSerializer
    user_model : class
        Reference to User model
    lookup_field : str
        Model field to extract model instance in detail and update views
    course : Course model instance
    '''

    serializer_class = LectureSerializer
    user_model = User
    lookup_field = 'id'
    course = None

    def init_lecture(self, admin_only=True):
        '''
        Initialize lecture view by fetching course.
        Course slug is in URL.

        Parameters
        --------------
        admin_only : boolean
            True if operation is performed by admin

        Raises
        --------------
        404 error:
            If course is not published or archived and admin_only=True
        '''
        course_slug = self.kwargs.get('slug', None)
        self.course = Course.objects.get_course_by_slug(
            course_slug,
            admin_only=admin_only
        )

    def check_lecture_permissions(self, request):
        '''
        Check user permissions
        - admin user has CRUD permissions
        - unauthenticated user has only list view permission
        - authenticated user not registered for course has only list view permission
        - authenticated user registered for course has list and detail view permission

        Parameters
        ----------------
        request : Request

        Raises
        ----------------
        403 error:
            If no credentials are passed
            If user asking for detail view is not registed for a course
        '''
        if request.user is None:
            logger.error('Lecture details accessed without credentials')
            raise CustomAPIError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Must be logged in to access a lecture'
            )
        if not request.user.is_staff and not CourseStudentRegistration.objects.is_student_registered(
            user=request.user,
            course=self.course
        ):
            logger.error('Unregistered student {} attempting to access lecture'.format(
                self.request.user.id
            ))
            raise CustomAPIError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Must register for the course to access a lecture'
            )

    def get_queryset(self):
        '''
        Fetch list of lectures for course

        Returns
        ------------
        List of lectures for a given course
        '''
        return Lecture.objects.filter(
            course=self.course
        )

    def get_object(self):
        '''
        Fetch lecture object

        Raises
        ---------------
        404 error:
            If lecture id does not exist in db

        Returns
        ---------------
        Lecture model instance with id in URL
        '''
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
    '''
    Lecture view for CRUD

    Methods
    -----------------
    get(request, *args, **kwargs)
        Handles list and detail views for lectures
    post(request, *args, **kwargs):
        Creates a new lecture
    patch(request, *args, **kwargs):
        Updates an exiting lecture
    delete(request, *args, **kwargs):
        Deletes a lecture
    '''

    def perform_update(self, serializer):
        '''
        When updating a lecture

        Parameters
        ---------------
        serializer : dict
            Data for updating lecture

        Raises
        ---------------
        400 error:
            If data is empty
            If new title is the same as another existing lecture
        403 error:
            If user is not logged in
            If user is not instructor
        404 error:
            If lecture being updated does not exist in db
        '''
        serializer.save(
            user=self.request.user,
            course=self.course
        )

    def get(self, request, *args, **kwargs):
        '''
        List and detail view for lectures

        Parameters
        --------------
        request : Request

        Raises
        --------------
        403 error:
            Unregistered user accessing lecture detail view
        404 error:
            If course not found
            If non-admin user accessing unpublished course
            If lecture cannot be found

        Returns
        -------------
        Array with lectures in a course or lecture details
        '''
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
        logger.info('Lecture {} accessed by user {}'.format(
            self.kwargs.get('id'),
            self.request.user.id
        ))
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        '''
        Creates a new lecture

        Parameters
        -------------
        request : Request

        Raises
        -------------
        400 error:
            Empty data
            Title is missing
            Title is duplicate
        403 error:
            User not logged in
            User not instructor for the course
        404 error:
            Course not found

        Returns
        -------------
        New lecture details
        '''
        self.authenticate(self.request)
        self.init_lecture()
        serializer = LectureSerializer(data=request.data)
        serializer.save(
            user=self.request.user,
            course=self.course
        )
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        '''
        Updates existing lecture

        Parameters
        -------------
        request : Request

        Raises
        -------------
        400 error:
            Empty data
            New title duplicate of another lecture in course
        403 error:
            User not logged in
            User not instructor for the course
        404 error:
            Course not found
            Lecture not found

        Returns
        -------------
        Updated lecture details
        '''
        self.authenticate(self.request)
        self.init_lecture()
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        '''
        Delete a lecture

        Parameters
        -------------
        request : Request

        Raises
        -------------
        403 error:
            User not logged in
            User not instructor for the course
        404 error:
            Course not found
            Lecture not found
        '''
        self.authenticate(self.request)
        self.init_lecture()
        if not self.course.check_user_is_instructor(request.user):
            logger.critical('Non instructor user {} attempting to delete lecture {}'.format(
                self.request.user.id,
                self.kwargs.get('id', None)
            ))
            raise CustomAPIError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Only an instructor can delete lectures'
            )
        return self.destroy(request, *args, **kwargs)


class AdjustLectureOrderView(LectureBaseView):
    '''
    Move a lecture up or down in a course

    Methods
    --------------
    post(request, *args, **kwargs):
        Moves the lecture
    '''

    def post(self, request, *args, **kwargs):
        '''
        Moves the lecture up or down in the lecture list of a course

        Parameters
        -------------
        request : Request

        Raises
        -------------
        400 error:
            First lecture is moved up
            Last lecture is moved down
            Direction of movement is not up or down
        403 error:
            User not logged in
            User is not an instructor of the course
        404 error:
            Course not found
            Lecture not found
        '''
        self.authenticate(self.request)
        self.init_lecture()
        if not self.course.check_user_is_instructor(request.user):
            logger.critical('Non instructor user {} moving lecture {}'.format(
                self.request.user.id,
                self.kwargs.get('id', None)
            ))
            raise CustomAPIError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Only an instructor can change the order of lectures'
            )
        lecture = self.get_object()
        Lecture.objects.change_lecture_order(
            lecture, self.kwargs.get('direction'))
        return Response()
