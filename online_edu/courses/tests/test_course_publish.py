import pytest
from rest_framework.test import APIClient

from user_auth.tests.fixtures import test_user, access_token
from courses.models import Course
from .fixtures import sample_course

pytestmark = pytest.mark.django_db


def test_publish_course_endpoint(test_user, access_token, sample_course):
    '''
    Test for updating a course by publishing it
    '''

    client = APIClient()

    user1 = test_user()
    user1.is_staff = True
    user1.save()
    course1 = sample_course()

    # Making user the instructor
    course1.add_instructor(user1)

    token = access_token(user1, 60)

    # Success - instructor can publish a course
    api_response = client.patch(
        f'/api/courses/{course1.slug}/publish',
        {
            'is_draft': 'False'
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 200

    updated_course = Course.objects.all()[0]
    assert updated_course.is_draft == False

    # Success - instructor can unpublish a course
    api_response = client.patch(
        f'/api/courses/{course1.slug}/publish',
        {
            'is_draft': 'True'
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 200

    updated_course = Course.objects.all()[0]
    assert updated_course.is_draft == True


def test_unauthorized_course_publishing(test_user, access_token, sample_course):
    '''
    Test for only an instructor can (un)publish a course
    '''

    client = APIClient()

    user1 = test_user()
    course1 = sample_course()
    token = access_token(user1, 60)

    # Fail - non-admin user cannot publish a course
    api_response = client.patch(
        f'/api/courses/{course1.slug}/publish',
        {
            'is_draft': 'False'
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 403

    # Fail - admin user not instructor cannot publish a course
    user1.is_staff = True
    user1.save()
    api_response = client.patch(
        f'/api/courses/{course1.slug}/publish',
        {
            'is_draft': 'False'
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Only an instructor of a course can update a course'

    # Making user the instructor
    course1.add_instructor(user1)

    # Fail - wrong course slug URL should give 404
    api_response = client.patch(
        f'/api/courses/{course1.slug+"1"}/publish',
        {
            'is_draft': 'False'
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'Course not found from URL'
