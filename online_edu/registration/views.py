from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework_simplejwt.exceptions import InvalidToken

from user_auth.models import User
from user_auth.views import UserAuthentication
from courses.models import Course
from courses.serializers import CourseSerializer
from courses.error_definitions import CourseGenericError
from .models import CourseStudentRegistration


class CourseRegisterView(UpdateAPIView, UserAuthentication):
    '''
    Register a student for a course and
    return list of courses for the student.
    '''

    serializer_class = CourseSerializer
    lookup_field = 'slug'
    user_model = User

    def get_queryset(self, *args, **kwargs):
        '''Return published courses'''
        return Course.objects.fetch_courses()

    def partial_update(self, request, *args, **kwargs):
        try:
            user = self.authenticate(request, check_admin=False)
            if user is not None:
                course_obj = self.get_object()
                CourseStudentRegistration.objects.register_student(
                    user=user,
                    course=course_obj
                )
                return Response(
                    data=CourseSerializer(
                        user.course_set.all(),
                        many=True
                    ).data
                )
            else:
                return Response(
                    data='Must be logged in to register for course',
                    status=status.HTTP_403_FORBIDDEN
                )
        except CourseGenericError as e:
            return Response(
                data=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )
        except InvalidToken as e:
            return Response(
                data='Must be logged in to register for course',
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            return Response(
                data=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )
