import pytest
import json
from rest_framework.test import APIClient

from courses.models import Course
from lectures.models import Lecture
from registration.models import CourseStudentRegistration
from user_auth.tests.fixtures import test_user, access_token
from courses.tests.fixtures import sample_course
from lectures.tests.fixtures import test_lecture, test_lectures
from video_contents.tests.fixtures import test_video

pytestmark = pytest.mark.django_db


def test_fetch_lecture_list(test_user, access_token, sample_course, test_lectures):
    '''List view test for lectures'''

    client = APIClient()

    # Create sample course
    course1 = sample_course()

    # Create lectures for the course
    lectures = test_lectures(course=course1, no_of_lectures=4)

    # Fail - as unpublished course lecture should not be listed
    api_response = client.get(
        f'/api/courses/{course1.slug}/lectures/',
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'Course not found'

    # Publish the course
    course1.is_draft = False
    course1.save()

    # Success - no credentials for fetching lecture list
    api_response = client.get(
        f'/api/courses/{course1.slug}/lectures/',
        format='json'
    )
    assert api_response.status_code == 200
    api_response.render()
    api_response.data = json.loads(api_response.content)
    assert len(api_response.data) == 4

    # Create sample user
    user1 = test_user()
    token1 = access_token(user1, 60)

    # Unpublish the course
    course1.is_draft = True
    course1.save()

    # Fail - non-admin user cannot access unpublished lectures
    api_response = client.get(
        f'/api/courses/{course1.slug}/lectures/',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'Course not found'

    # Making user admin
    user1.is_staff = True
    user1.save()

    # Admin can fetch lectures of unpublished courses
    api_response = client.get(
        f'/api/courses/{course1.slug}/lectures/',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 200
    api_response.render()
    api_response.data = json.loads(api_response.content)
    assert len(api_response.data) == 4


def test_fetch_lecture(test_user, access_token, sample_course, test_lectures, test_video):
    '''Detail view test for lecture'''

    client = APIClient()

    # Create sample course
    course1 = sample_course()

    # Create lectures for the course
    lectures = test_lectures(course=course1, no_of_lectures=2)

    # Fail - as unpublished course lecture should not be listed
    api_response = client.get(
        f'/api/courses/{course1.slug}/lectures/{lectures[0].id}',
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'Course not found'

    api_response = client.get(
        f'/api/courses/{course1.slug}/lectures/{lectures[1].id}',
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'Course not found'

    # Publish the course
    course1.is_draft = False
    course1.save()

    # Fail - without credentials lecture details should not listed
    api_response = client.get(
        f'/api/courses/{course1.slug}/lectures/{lectures[0].id}',
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Must be logged in to access a lecture'

    api_response = client.get(
        f'/api/courses/{course1.slug}/lectures/{lectures[1].id}',
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Must be logged in to access a lecture'

    # Create sample user
    user1 = test_user()
    user1.is_active = True
    user1.save()
    token1 = access_token(user1, 60)

    # Fail - unregistered student cannot access lecture details
    api_response = client.get(
        f'/api/courses/{course1.slug}/lectures/{lectures[0].id}',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Must register for the course to access a lecture'

    # Register student for course
    CourseStudentRegistration.objects.register_student(user1, course1)

    # Success
    api_response = client.get(
        f'/api/courses/{course1.slug}/lectures/{lectures[0].id}',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert api_response.data['title'] == lectures[0].title
    assert len(api_response.data['videos']) == 0

    # Adding videos to lecture 1
    lecture1_video1 = test_video(course=course1, name='Lec 1 video 1')
    lecture1_video2 = test_video(course=course1, name='Lec 1 video 2')
    Lecture.objects.add_video_to_lecture(lectures[0].id, lecture1_video1)
    Lecture.objects.add_video_to_lecture(lectures[0].id, lecture1_video2)

    # Success - lecture detail view should contain video list
    api_response = client.get(
        f'/api/courses/{course1.slug}/lectures/{lectures[0].id}',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert api_response.data['title'] == lectures[0].title
    assert len(api_response.data['videos']) == 2

    # Unpublish the course
    course1.is_draft = True
    course1.save()

    api_response = client.get(
        f'/api/courses/{course1.slug}/lectures/{lectures[0].id}',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'Course not found'

    # Make user admin
    user1.is_staff = True
    user1.save()

    api_response = client.get(
        f'/api/courses/{course1.slug}/lectures/{lectures[1].id}',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert api_response.data['title'] == lectures[1].title
    assert len(api_response.data['videos']) == 0

    # Adding videos to lecture 2
    lecture2_video1 = test_video(course=course1, name='Lec 2 video 1')
    lecture2_video2 = test_video(course=course1, name='Lec 2 video 2')
    lecture2_video3 = test_video(course=course1, name='Lec 2 video 3')
    Lecture.objects.add_video_to_lecture(lectures[1].id, lecture2_video1)
    Lecture.objects.add_video_to_lecture(lectures[1].id, lecture2_video2)
    Lecture.objects.add_video_to_lecture(lectures[1].id, lecture2_video3)

    api_response = client.get(
        f'/api/courses/{course1.slug}/lectures/{lectures[1].id}',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert api_response.data['title'] == lectures[1].title
    assert len(api_response.data['videos']) == 3
