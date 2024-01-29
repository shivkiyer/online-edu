import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.exceptions import InvalidToken

from user_auth.models import User
from user_auth.views import UserAuthentication
from courses.models import Course
from courses.serializers import CourseSerializer
from courses.views import CourseBaseView
from common.error_definitions import DEFAULT_ERROR_RESPONSE, \
    Http400Error, \
    Http403Error, \
    Http404Error
from .models import CourseStudentRegistration

logger = logging.getLogger(__name__)


class CourseRegisterView(CourseBaseView):
    '''
    Register a student for a course and
    return list of courses for the student.
    '''

    def get_queryset(self, *args, **kwargs):
        '''Return published courses'''
        return Course.objects.fetch_courses()

    def post(self, request, *args, **kwargs):
        try:
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
        except Http400Error as e:
            logger.error('Error registering student - {}'.format(str(e)))
            return Response(
                data=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Http403Error as e:
            logger.error('Error registering student - {}'.format(str(e)))
            return Response(
                data=str(e),
                status=status.HTTP_403_FORBIDDEN
            )
        except Http404Error as e:
            logger.error('Error registering student - {}'.format(str(e)))
            return Response(
                data=str(e),
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.critical('Error registering student {}'.format(str(e)))
            return Response(
                data=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )


class CourseInstructorAddView(CourseBaseView):
    '''Add an instructor to a course'''

    def get_queryset(self, *args, **kwargs):
        '''Return published courses'''
        if self.request.user is not None and self.request.user.is_staff:
            return Course.objects.all()
        else:
            raise Http403Error('Must be logged in as an instructor')

    def post(self, request, *args, **kwargs):
        try:
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
                raise Http403Error('Must be logged in as an instructor')
        except Http403Error as e:
            logger.error('Error adding instructor {}'.format(str(e)))
            return Response(
                data=str(e),
                status=status.HTTP_403_FORBIDDEN
            )
        except Http400Error as e:
            logger.error('Error adding instructor {}'.format(str(e)))
            return Response(
                data=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Http404Error as e:
            logger.error('Error adding instructor {}'.format(str(e)))
            return Response(
                data=str(e),
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.critical('Error adding instructor {}'.format(str(e)))
            return Response(
                data=DEFAULT_ERROR_RESPONSE,
                status=status.HTTP_400_BAD_REQUEST
            )
