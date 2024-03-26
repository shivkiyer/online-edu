from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import status

from common.error_definitions import CustomAPIError
from .models import VideoContent
from courses.models import Course
from lectures.models import Lecture
from user_auth.models import User
from user_auth.views import UserAuthentication
from .serializers import VideoContentSerializer


class VideoContentView(APIView, UserAuthentication):
    '''
    View for uploading videos

    Attributes
    -----------------
    parser_classes : list
        FormParser and MultiPartParser used for file uploads

    Methods
    -----------------
    post(request, filename, *args, **kwargs):
        Creates VideoContent model instance and handles file uploads
    '''

    parser_classes = [FormParser, MultiPartParser, ]
    user_model = User

    def post(self, request, filename, *args, **kwargs):
        '''
        Creates VideoContent model instance and handles file uploads

        Parameters
        ---------------
        request : Request object
        filename : str
            Name of the video file

        Raises
        ---------------
        400 error:
            If course slug is not present in url
            If video name is not provided in request body
            If video name is not unique
        403 error:
            If no credentials are provided in header
            If non-admin credentials are provided in header
            If non-instructor credentials are provided in header
        404 error:
            If lecture cannot be found

        Returns
        ---------------
        201
        '''
        user = self.authenticate(request)
        file_obj = request.data['File']

        course_slug = self.kwargs.get('slug', None)
        course_obj = Course.objects.get_course_by_slug(
            course_slug,
            admin_only=True
        )
        if not course_obj.check_user_is_instructor(user):
            raise CustomAPIError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Only an instructor can add videos'
            )

        video_name = request.data.get('name')
        if video_name is None:
            raise CustomAPIError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Video name is required'
            )

        VideoContent.objects.is_video_name_unique(video_name)

        video_obj = VideoContent.objects.create(
            name=video_name,
            course=course_obj,
            video_file=file_obj
        )

        lecture_id = self.kwargs.get('id')
        Lecture.objects.add_video_to_lecture(lecture_id, video_obj)

        serializer = VideoContentSerializer(video_obj)

        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )
