from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import status

from common.error_definitions import CustomAPIError
from .models import VideoContent
from courses.models import Course
from lectures.models import Lecture


class VideoContentView(APIView):
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
        404 error:
            If lecture cannot be found

        Returns
        ---------------
        201
        '''
        file_obj = request.data['File']

        course_slug = self.kwargs.get('slug', None)
        course_obj = Course.objects.get_course_by_slug(
            course_slug,
            admin_only=True
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

        return Response(status=status.HTTP_201_CREATED)
