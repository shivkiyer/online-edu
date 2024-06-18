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


def test_list_courses_with_lang(sample_courses):
    '''Tests whether language specific course content is returned'''

    client = APIClient()

    courses = sample_courses(5)

    # Publish all courses
    for course in courses:
        course.is_draft = False
        course.save()

    # Asking for content in language that does not exist
    # should return default language content
    api_response = client.get(
        '/api/courses/',
        headers={
            'Accept-Language': 'de'
        },
        format='json'
    )
    assert api_response.status_code == 200
    api_response.render()
    api_response = json.loads(api_response.content)
    assert len(api_response) == 5
    assert api_response[0]['title'] == 'Course 1'
    assert api_response[1]['title'] == 'Course 2'
    assert api_response[2]['title'] == 'Course 3'
    assert api_response[3]['title'] == 'Course 4'
    assert api_response[4]['title'] == 'Course 5'

    for course in courses:
        course.title_de = f'{course.title} - German'
        course.save()

    # Fetching supported language content will return
    # data when present in that language or else
    # in default language
    api_response = client.get(
        '/api/courses/',
        headers={
            'Accept-Language': 'de'
        },
        format='json'
    )
    assert api_response.status_code == 200
    api_response.render()
    api_response = json.loads(api_response.content)
    assert len(api_response) == 5
    assert api_response[0]['title'] == 'Course 1 - German'
    assert api_response[1]['title'] == 'Course 2 - German'
    assert api_response[2]['title'] == 'Course 3 - German'
    assert api_response[3]['title'] == 'Course 4 - German'
    assert api_response[4]['title'] == 'Course 5 - German'
    assert api_response[0]['description'] == 'Course description 1'
    assert api_response[1]['description'] == 'Course description 2'
    assert api_response[2]['description'] == 'Course description 3'
    assert api_response[3]['description'] == 'Course description 4'
    assert api_response[4]['description'] == 'Course description 5'

    # Fetching content in unsupported language should
    # return content in default language
    api_response = client.get(
        '/api/courses/',
        headers={
            'Accept-Language': 'pt'
        },
        format='json'
    )
    assert api_response.status_code == 200
    api_response.render()
    api_response = json.loads(api_response.content)
    assert len(api_response) == 5
    assert api_response[0]['title'] == 'Course 1'
    assert api_response[1]['title'] == 'Course 2'
    assert api_response[2]['title'] == 'Course 3'
    assert api_response[3]['title'] == 'Course 4'
    assert api_response[4]['title'] == 'Course 5'

    # Country specific content should return language content
    api_response = client.get(
        '/api/courses/',
        headers={
            'Accept-Language': 'de_CH'
        },
        format='json'
    )
    assert api_response.status_code == 200
    api_response.render()
    api_response = json.loads(api_response.content)
    assert len(api_response) == 5
    assert api_response[0]['title'] == 'Course 1 - German'
    assert api_response[1]['title'] == 'Course 2 - German'
    assert api_response[2]['title'] == 'Course 3 - German'
    assert api_response[3]['title'] == 'Course 4 - German'
    assert api_response[4]['title'] == 'Course 5 - German'


def test_course_detail_with_lang(test_user, access_token, sample_course):
    '''Test that detail course view should handle language content'''

    client = APIClient()

    user1 = test_user(is_staff=True)

    token = access_token(user1, 60)

    course = sample_course()

    # Returns default language content due
    # to auto-populate function
    api_response = client.get(
        f'/api/courses/{course.slug}',
        headers={
            'Authorization': f'Bearer {token}',
            'Accept-Language': 'de'
        },
        format='json'
    )
    assert api_response.data['title'] == 'Course 1'
    assert api_response.data['description'] == 'Course description 1'

    course.title_de = 'Course 1 - German translation'
    course.save()

    # Returns correct language
    api_response = client.get(
        f'/api/courses/{course.slug}',
        headers={
            'Authorization': f'Bearer {token}',
            'Accept-Language': 'de'
        },
        format='json'
    )
    assert api_response.data['title'] == 'Course 1 - German translation'
    assert api_response.data['description'] == 'Course description 1'

    # With country specific language
    api_response = client.get(
        f'/api/courses/{course.slug}',
        headers={
            'Authorization': f'Bearer {token}',
            'Accept-Language': 'de-DE'
        },
        format='json'
    )
    assert api_response.data['title'] == 'Course 1 - German translation'
    assert api_response.data['description'] == 'Course description 1'

    # Reverts to default if requested language not supported
    api_response = client.get(
        f'/api/courses/{course.slug}',
        headers={
            'Authorization': f'Bearer {token}',
            'Accept-Language': 'fr'
        },
        format='json'
    )
    assert api_response.data['title'] == 'Course 1'
    assert api_response.data['description'] == 'Course description 1'
