import pytest
import os
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile

from django.conf import settings
from courses.models import Course
from video_contents.models import VideoContent
from user_auth.tests.fixtures import test_user, access_token
from courses.tests.fixtures import sample_course
from lectures.tests.fixtures import test_lectures
from common.file_handling import clean_test_media

pytestmark = pytest.mark.django_db


def test_add_video_api(test_user, access_token, test_lectures):
    '''Test for uploading video to a lecture'''

    client = APIClient()

    # Test user
    user1 = test_user()
    user1.is_staff = True
    user1.save()

    # Test course
    course1 = Course.objects.create(
        title='Some course matter',
        description='Course descr',
        is_free=True
    )
    course1.add_instructor(user1)

    # JWT
    token1 = access_token(user1, 60)

    # Test lectures for course
    lectures = test_lectures(course1, 3)

    # Test file
    test_file = SimpleUploadedFile('somefile.txt', b'Some text')

    # Success - video uploaded
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/{lectures[0].id}/videos/add-video/somefile.txt',
        {
            'name': 'Some file',
            'File': test_file
        },
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='multipart'
    )
    assert api_response.status_code == 201
    videos = VideoContent.objects.all()
    assert videos.count() == 1
    assert videos[0].video_file.name == 'somecoursematter/somefile.txt'
    video_path = os.path.join(
        f'{settings.BASE_DIR}',
        'test_media',
        'somecoursematter',
        'somefile.txt'
    )
    assert os.path.exists(video_path)
    assert len(lectures[0].videos.all()) == 1
    assert lectures[0].videos.all()[0].id == videos[0].id

    # Delete uploaded file
    clean_test_media()


def test_unauthorized_add_video_(test_user, access_token, test_lectures):
    '''Test unauthoized upload of videos'''

    client = APIClient()

    # Test user
    user1 = test_user()

    # Test course
    course1 = Course.objects.create(
        title='Some course matter',
        description='Course descr',
        is_free=True
    )

    # Test lectures for course
    lectures = test_lectures(course1, 3)

    # Test file
    test_file = SimpleUploadedFile('somefile.txt', b'Some text')

    # Fail - no user credentials
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/{lectures[0].id}/videos/add-video/somefile.txt',
        {
            'name': 'Some file',
            'File': test_file
        },
        format='multipart'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Invalid login or inactive account'

    # JWT
    token1 = access_token(user1, 60)

    # Fail - non-admin credentials
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/{lectures[0].id}/videos/add-video/somefile.txt',
        {
            'name': 'Some file',
            'File': test_file
        },
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='multipart'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Admin privileges required for this action'

    # Make user admin
    user1.is_staff = True
    user1.save()

    # Fail - user is not instructor
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/{lectures[0].id}/videos/add-video/somefile.txt',
        {
            'name': 'Some file',
            'File': test_file
        },
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='multipart'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Only an instructor can add videos'

    # Delete uploaded file
    clean_test_media()


def test_add_video_with_same_name(test_user, access_token, test_lectures):
    '''Test for preventing multiple videos with same name'''

    client = APIClient()

    # Test user
    user1 = test_user()
    user1.is_staff = True
    user1.save()

    # JWT
    token1 = access_token(user1, 60)

    # Test course
    course1 = Course.objects.create(
        title='Some course matter',
        description='Course descr',
        is_free=True
    )

    # Make test user instructor
    course1.add_instructor(user1)

    # Test lectures for course
    lectures = test_lectures(course1, 3)

    # Test file
    test_file = SimpleUploadedFile('somefile.txt', b'Some text')

    # Upload video
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/{lectures[0].id}/videos/add-video/somefile.txt',
        {
            'name': 'Some file',
            'File': test_file
        },
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='multipart'
    )
    assert api_response.status_code == 201

    # Fail - uploading video with same name
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/{lectures[0].id}/videos/add-video/somefile.txt',
        {
            'name': 'Some file',
            'File': test_file
        },
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='multipart'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'Another video with the same name already exists'

    # Delete uploaded file
    clean_test_media()
