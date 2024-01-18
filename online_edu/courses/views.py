import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.mixins import ListModelMixin, \
    RetrieveModelMixin, \
    UpdateModelMixin

from user_auth.models import User
from user_auth.views import UserAuthentication
from .models import Course
from .serializers import CourseSerializer
from common.error_definitions import DEFAULT_ERROR_RESPONSE, Http400Error, Http403Error

logger = logging.getLogger(__name__)


class CourseView(
    CreateAPIView,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    UserAuthentication
):
    '''CRUD operations on Course'''

    serializer_class = CourseSerializer
    user_model = User
    lookup_field = 'slug'

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
                course=course.title,
                user=self.request.user.username
            )
        )

    def perform_update(self, serializer):
        '''Update a course by an authenticated instructor'''
        course = serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        '''Create a new course - POST request'''
        try:
            self.authenticate(request)
            serializer = self.get_serializer(data=request.data)
            self.perform_create(serializer)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        except Http400Error as e:
            logger.error('Error creating course - {}'.format(str(e)))
            return Response(
                data=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Http403Error as e:
            logger.critical('Course creation by non admin attempted')
            return Response(
                data=str(e),
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            logger.critical('Error creating course - {}'.format(str(e)))
            return Response(
                data=DEFAULT_ERROR_RESPONSE,
                status=status.HTTP_400_BAD_REQUEST
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
        try:
            self.authenticate(request)
            return self.partial_update(request, *args, **kwargs)
        except Http400Error as e:
            logger.error('Error updating course for url {url} - {error}'.format(
                url=request.get_full_path(),
                error=str(e)
            ))
            return Response(
                data=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Http403Error as e:
            logger.critical('Course update by non admin attempted for url {}'.format(
                request.get_full_path()))
            return Response(
                data=str(e),
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            logger.critical('Error updating course for url {url} - {error}'.format(
                url=request.get_full_path(),
                error=str(e)
            ))
            return Response(
                data=DEFAULT_ERROR_RESPONSE,
                status=status.HTTP_400_BAD_REQUEST
            )
