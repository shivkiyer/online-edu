from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin

from user_auth.models import User
from user_auth.views import UserAuthentication
from courses.models import Course
from common.error_definitions import Http400Error, \
    Http401Error, \
    Http403Error, \
    Http404Error, \
    DEFAULT_ERROR_RESPONSE
from .serializers import LectureSerializer


class LectureBaseView(GenericAPIView, UserAuthentication):
    '''Basic lecture view'''

    serializer_class = LectureSerializer
    user_model = User
    lookup_field = 'id'


class LectureView(LectureBaseView, CreateModelMixin):
    '''Basic lecture view'''

    def get(self, request, *args, **kwargs):
        return Response('TODO')

    def post(self, request, *args, **kwargs):
        course_slug = self.kwargs.get('slug', None)
        try:
            course_obj = Course.objects.get_course_by_slug(course_slug)
            self.authenticate(request)
            serializer = LectureSerializer(data=request.data)
            serializer.save(
                user=self.request.user,
                course=course_obj
            )
            return Response(serializer.data)
        except Http400Error as e:
            return Response(
                data=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Http403Error as e:
            return Response(
                data=str(e),
                status=status.HTTP_403_FORBIDDEN
            )
        except Http404Error as e:
            return Response(
                data=str(e),
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception:
            return Response(
                data=DEFAULT_ERROR_RESPONSE,
                status=status.HTTP_400_BAD_REQUEST
            )
