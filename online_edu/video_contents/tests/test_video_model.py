import pytest
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from video_contents.models import VideoContent
from courses.models import Course
from courses.tests.fixtures import sample_course
from lectures.tests.fixtures import test_lectures
from common.file_handling import clean_test_media

pytestmark = pytest.mark.django_db


def test_video_model():
    '''Test for creation of video model instance'''

    course1 = Course.objects.create(
        title='Course 1',
        description='Course 1 description',
        is_free=True
    )

    test_file = SimpleUploadedFile('lec1.txt', b'Some text')

    video1 = VideoContent.objects.create(
        course=course1,
        name='Video 1',
        video_file=test_file
    )

    assert os.path.exists(video1.video_file.path)
    assert video1.video_file.name == 'course1/lec1.txt'

    # Clean test media root folder
    clean_test_media()


def test_video_file_paths():
    '''Test that video files are uploaded by course directories'''

    course1 = Course.objects.create(
        title='Course 1',
        description='Course 1 description',
        is_free=True
    )
    course2 = Course.objects.create(
        title='Course 2',
        description='Course 2 description',
        is_free=True
    )

    file1 = SimpleUploadedFile(
        'lec1course1.txt',
        b'Lec 1 for course 1'
    )
    file2 = SimpleUploadedFile(
        'lec1course2.txt',
        b'Lec 1 for course 2'
    )

    video_file1 = VideoContent.objects.create(
        course=course1,
        name='Video 1 of course 1',
        video_file=file1
    )
    video_file2 = VideoContent.objects.create(
        course=course2,
        name='Video 1 of course 2',
        video_file=file2
    )

    assert os.path.exists(os.path.join(
        settings.MEDIA_ROOT, 'course1', 'lec1course1.txt'))
    assert os.path.exists(os.path.join(
        settings.MEDIA_ROOT, 'course2', 'lec1course2.txt'))

    # Clean test media root folder
    clean_test_media()
