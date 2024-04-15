import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from video_contents.models import VideoContent


pytestmark = pytest.mark.django_db


@pytest.fixture
def test_video():
    '''Create a test VideoContent model instance'''

    def _gen_video_content(
            course,
            name=None,
            file_name=None,
            video_file=None
    ):
        if name is None:
            name = 'Some video file'
        if file_name is None:
            file_name = 'some_file.txt'
        if video_file is None:
            video_file = SimpleUploadedFile(file_name, b'Some file contents')

        return VideoContent.objects.create(
            course=course,
            name=name,
            video_file=video_file
        )

    return _gen_video_content
