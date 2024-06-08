import pytest
from rest_framework.test import APIClient

from courses.tests.fixtures import sample_course
from user_auth.tests.fixtures import test_user, access_token
from lectures.models import Lecture

pytestmark = pytest.mark.django_db


def test_lecture_delete_endpoint(sample_course, test_user, access_token):
    '''Tests for deleting a lecture'''

    client = APIClient()

    user1 = test_user()
    user1.is_staff = True
    user1.save()

    token1 = access_token(user1, 60)

    # Create test course
    course1 = sample_course

    course1.add_instructor(user1)

    # Create test lecture in test course
    lecture1 = Lecture.objects.create(title='Lecture 1', course=course1)

    # Success
    api_response = client.delete(
        f'/api/courses/{course1.slug}/lectures/{lecture1.id}',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 204
    assert Lecture.objects.all().count() == 0


def test_unauthorized_lecture_delete(sample_course, test_user, access_token):
    '''Tests to verify only an instructor can delete a lecture'''

    client = APIClient()

    # Create test course
    course1 = sample_course

    # Create test lecture in test course
    lecture1 = Lecture.objects.create(title='Lecture 1', course=course1)

    # Fail - no credentials passed
    api_response = client.delete(
        f'/api/courses/{course1.slug}/lectures/{lecture1.id}',
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Invalid login or inactive account'

    # Create non-admin test user
    user1 = test_user()
    token1 = access_token(user1, 60)

    # Fail - credentials of non-admin user passed
    api_response = client.delete(
        f'/api/courses/{course1.slug}/lectures/{lecture1.id}',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Admin privileges required for this action'

    # Make user admin
    user1.is_staff = True
    user1.save()

    # Fail - user must be instructor to delete lectures
    api_response = client.delete(
        f'/api/courses/{course1.slug}/lectures/{lecture1.id}',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Only an instructor can delete lectures'
