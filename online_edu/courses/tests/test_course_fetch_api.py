import pytest
import json
from rest_framework.test import APIClient

from courses.models import Course
from .fixtures import sample_course, sample_courses
from user_auth.tests.fixtures import test_user, access_token

pytestmark = pytest.mark.django_db


def test_user_course_list_view(sample_courses):
    '''
    Test that a normal user can only see published courses
    and not draft or archived courses in list view.
    '''

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


def test_admin_list_view(sample_courses, test_user, access_token):
    '''
    Test that an admin user can view all courses in list view
    '''

    client = APIClient()

    # Create sample courses - all in draft mode
    courses = sample_courses(5)

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

    # Make second course not draft
    courses[1].is_draft = False
    courses[1].save()

    # Make third course not draft
    courses[2].is_draft = False
    courses[2].save()

    # Make fourth course not draft but archived
    courses[2].is_draft = False
    courses[3].is_archived = True
    courses[2].save()

    api_response = client.get(
        '/api/courses/',
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert len(api_response.data) == 5


def test_user_course_detail_view(sample_course, test_user, access_token):
    '''
    Test that a regular user can only view details of
    published courses
    '''

    client = APIClient()
    user1 = test_user()
    user1.is_staff = False
    user1.save()
    token = access_token(user1, 60)

    # Sample draft course
    course = sample_course()

    # Should give 404 as course is in draft mode
    api_response = client.get(
        f'/api/courses/{course.slug}',
        format='json'
    )
    assert api_response.data['detail'] == 'Course not found from URL'
    assert api_response.status_code == 404

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


def test_admin_course_detail_view(sample_course, test_user, access_token):
    '''
    Test that admin user can view details of any course
    '''

    client = APIClient()
    user1 = test_user()
    user1.is_staff = True
    user1.save()
    token = access_token(user1, 60)

    # Sample draft course
    course = sample_course()

    # Admin user should be able to see a course in draft status
    api_response = client.get(
        f'/api/courses/{course.slug}',
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 200

    # Publish course
    course.is_draft = False
    course.save()
    api_response = client.get(
        f'/api/courses/{course.slug}',
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 200

    # Make course archived
    course.is_archived = True
    course.save()

    # Admin user should be able to see archived course
    api_response = client.get(
        f'/api/courses/{course.slug}',
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 200
