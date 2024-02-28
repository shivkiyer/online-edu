import logging
from rest_framework.response import Response
from rest_framework import status

from user_auth.models import User
from courses.models import Course
from courses.serializers import CourseSerializer
from courses.views import CourseBaseView
from common.error_definitions import DEFAULT_ERROR_RESPONSE, \
    CustomAPIError
from .models import CourseStudentRegistration

logger = logging.getLogger(__name__)


class CourseRegisterView(CourseBaseView):
    '''
    Register a student for a course and
    return list of courses for the student.

    Methods
    ------------
    get_queryset(self, *args, **kwargs):
        Returns list of published courses
    post(self, request, *args, **kwargs):
        Register user for course
    '''

    def get_queryset(self, *args, **kwargs):
        '''Return published courses'''
        return Course.objects.fetch_courses()

    def post(self, request, *args, **kwargs):
        '''
        Register user for a course

        Parameters
        --------------
        request : Request

        Raises
        --------------
        400 error
            If user is already registered for course
        403 error
            If user is not registered
        404 error
            If course is not found or course is not published

        Returns
        -------------
        List of courses that user has registered for
        '''
        user = self.authenticate(request, check_admin=False)
        course_obj = self.get_object()
        CourseStudentRegistration.objects.register_student(
            user=user,
            course=course_obj
        )
        logger.info('Registering student {student} for course {course}'.format(
            student=user.id,
            course=course_obj.id
        ))
        return Response(
            data=CourseSerializer(
                user.course_set.all(),
                many=True
            ).data
        )


class CourseInstructorAddView(CourseBaseView):
    '''
    Add an instructor to a course

    Methods
    --------------
    get_queryset(self, *args, **kwargs):
        Returns list of all courses
    post(self, request, *args, **kwargs):
        Add an instructor to a course
    '''

    def get_queryset(self, *args, **kwargs):
        '''
        Return published courses

        Raises
        --------------
        403 error
            If user is not admin

        Returns
        --------------
        List of all courses
        '''
        if self.request.user is not None and self.request.user.is_staff:
            return Course.objects.all()
        else:
            raise CustomAPIError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Must be logged in as an instructor'
            )

    def post(self, request, *args, **kwargs):
        '''
        Registers a user for a course

        Parameters
        ---------------
        request : Request

        Raises
        ---------------
        400 error:
            New instructor is already an instructor
        403 error:
            If user making addition is not an instructor
            New instructor is not admin
        404 error:
            Course not found
        '''
        user = self.authenticate(request)
        course_obj = self.get_object()
        if user is not None and course_obj.check_user_is_instructor(user):
            new_user = User.objects.get_user_by_email(
                request.data.get('email'))
            course_obj.add_instructor(new_user)
            logger.info('Added instructor {teacher} to course {course}'.format(
                teacher=new_user.id,
                course=course_obj.id
            ))
            return Response()
        else:
            raise CustomAPIError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Must be logged in as an instructor'
            )
