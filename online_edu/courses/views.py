import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import InvalidToken

from user_auth.models import User
from .models import Course
from .serializers import CourseSerializer
from common.error_definitions import DEFAULT_ERROR_RESPONSE
from common.error_handling import rest_framework_validation_error

logger = logging.getLogger(__name__)


class CourseCreateView(CreateAPIView, JWTAuthentication):
    '''Create a course with logged-in user as instructor'''

    serializer_class = CourseSerializer
    user_model = User

    def perform_create(self, serializer):
        course = serializer.save()
        course.add_instructor(self.request.user)
        logger.info(
            'Creating course {course} by user {user}'.format(
                course=course.title,
                user=self.request.user.username
            )
        )

    def create(self, request, *args, **kwargs):
        try:
            user = self.authenticate(request)
            if user is not None and user[0].is_staff:
                request.user = user[0]
                return super().create(request, *args, **kwargs)
            else:
                logger.critical('Course creation by non admin attempted')
                return Response(
                    data='Must be logged in as administrator to create a course',
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
