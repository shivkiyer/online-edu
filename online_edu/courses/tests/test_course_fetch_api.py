import pytest
import json
from rest_framework.test import APIClient

from courses.models import Course
from .fixtures import sample_course, sample_courses
from user_auth.tests.fixtures import test_user, access_token

pytestmark = pytest.mark.django_db


def test_course_fetch_all(sample_courses, test_user, access_token):
    '''Test get all courses endpoint'''

    client = APIClient()

    # Create sample courses - all in draft mode
    courses = sample_courses(5)

    # No course returned - all in draft
    api_response = client.get('/api/courses/', format='json')
    assert api_response.status_code == 200
    assert len(api_response.data) == 0

    # Make second course not draft
    courses[1].is_draft = False
    courses[1].save()

    # One course returned
    api_response = client.get('/api/courses/', format='json')
    assert api_response.status_code == 200
    assert len(api_response.data) == 1
    api_response.render()
    api_response = json.loads(api_response.content)
    assert api_response[0]['title'] == courses[1].title

    # Make fourth course not draft
    courses[3].is_draft = False
    courses[3].save()

    # Two courses returned
    api_response = client.get('/api/courses/', format='json')
    assert api_response.status_code == 200
    assert len(api_response.data) == 2
    api_response.render()
    api_response = json.loads(api_response.content)
    assert api_response[0]['title'] == courses[1].title
    assert api_response[1]['title'] == courses[3].title

    # Make last course not draft
    courses[4].is_draft = False
    courses[4].save()

    # Three courses returned
    api_response = client.get('/api/courses/', format='json')
    assert api_response.status_code == 200
    assert len(api_response.data) == 3
    api_response.render()
    api_response = json.loads(api_response.content)
    assert api_response[0]['title'] == courses[1].title
    assert api_response[1]['title'] == courses[3].title
    assert api_response[2]['title'] == courses[4].title

    # Make fourth course as archived
    courses[3].is_archived = True
    courses[3].save()

    # Two courses should be returned
    api_response = client.get('/api/courses/', format='json')
    assert api_response.status_code == 200
    assert len(api_response.data) == 2
    api_response.render()
    api_response = json.loads(api_response.content)
    assert api_response[0]['title'] == courses[1].title
    assert api_response[1]['title'] == courses[4].title

    # An admin user should be able to see all courses
    user1 = test_user()
    user1.is_staff = True
    user1.save()
    token = access_token(user1, 60)
    api_response = client.get(
        '/api/courses/',
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert len(api_response.data) == 5


def test_course_fetch_detail(sample_course, test_user, access_token):
    '''Test retrieve course endpoint'''

    client = APIClient()
    user1 = test_user()
    user1.is_staff = True
    user1.save()
    token = access_token(user1, 60)

    # Sample draft course
    course = sample_course

    # Should give 404 as course is in draft mode
    api_response = client.get(
        f'/api/courses/{course.slug}',
        format='json'
    )
    assert api_response.data['detail'] == 'Course not found from URL'
    assert api_response.status_code == 404

    # Admin user should be able to see a course in draft status
    api_response = client.get(
        f'/api/courses/{course.slug}',
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 200

    # Set draft to false
    course.is_draft = False
    course.save()
    # Should be retrieved
    api_response = client.get(
        f'/api/courses/{course.slug}',
        format='json'
    )
    assert api_response.status_code == 200
    assert api_response.data['title'] == course.title

    # Use wrong slug
    api_response = client.get(
        f'/api/courses/{course.slug + "1"}',
        format='json'
    )
    assert api_response.data['detail'] == 'Course not found from URL'
    assert api_response.status_code == 404

    # Make course archived
    course.is_archived = True
    course.save()
    # Should give 404
    api_response = client.get(
        f'/api/courses/{course.slug}',
        format='json'
    )
    assert api_response.data['detail'] == 'Course not found from URL'
    assert api_response.status_code == 404

    # Admin user should be able to see archived course
    api_response = client.get(
        f'/api/courses/{course.slug}',
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 200
