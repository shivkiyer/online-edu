import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import InvalidToken

from user_auth.models import User
from user_auth.views import UserAuthentication
from .models import Course
from .serializers import CourseSerializer
from .error_definitions import CourseGenericError, CourseForbiddenError
from common.error_definitions import DEFAULT_ERROR_RESPONSE
from common.error_handling import rest_framework_validation_error

logger = logging.getLogger(__name__)


class CourseView(
    CreateAPIView,
    ListModelMixin,
    RetrieveModelMixin,
    UserAuthentication
):
    '''Create a course with logged-in user as instructor'''

    serializer_class = CourseSerializer
    user_model = User
    lookup_field = 'slug'

    def get_queryset(self, *args, **kwargs):
        return Course.objects.fetch_courses()

    def perform_create(self, serializer):
        course = serializer.save(user=self.request.user)
        logger.info(
            'Creating course {course} by user {user}'.format(
                course=course.title,
                user=self.request.user.username
            )
        )

    def create(self, request, *args, **kwargs):
        try:
            self.authenticate(request)
            return super().create(request, *args, **kwargs)
        except CourseGenericError as e:
            logger.error('Error creating course - {}'.format(str(e)))
            return Response(
                data=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )
        except CourseForbiddenError as e:
            logger.critical('Course creation by non admin attempted')
            return Response(
                data=str(e),
                status=status.HTTP_403_FORBIDDEN
            )
        except ValidationError as e:
            logger.error('Error creating course - {}'.format(str(e)))
            return rest_framework_validation_error(e, 'Course could not be created')
        except InvalidToken as e:
            logger.critical('Course creation by non admin attempted')
            return Response(
                data='Must be logged in as administrator to create a course',
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            logger.critical('Error creating course - {}'.format(str(e)))
            return Response(
                data=DEFAULT_ERROR_RESPONSE,
                status=status.HTTP_400_BAD_REQUEST
            )

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug', None)
        if slug:
            return self.retrieve(request, *args, *kwargs)
        else:
            return self.list(request, *args, **kwargs)
