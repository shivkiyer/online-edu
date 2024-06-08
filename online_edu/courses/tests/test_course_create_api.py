import pytest
import time
from rest_framework.test import APIClient

from user_auth.tests.fixtures import test_user, access_token
from courses.models import Course

pytestmark = pytest.mark.django_db


def test_course_creation_endpoint(test_user, access_token):
    '''
    Tests for creating new course
    '''

    client = APIClient()

    user1 = test_user()
    user1.is_staff = True
    user1.save()

    token = access_token(user1, 60)

    # Success - admin user creates a new course
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Some course title',
            'description': 'Some course description',
            'price': 3.99
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 201
    assert Course.objects.count() == 1

    # Success - another course with different title
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Another course title',
            'description': 'Some course description',
            'price': 3.99
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 201
    assert Course.objects.count() == 2

    # Success - a free course with new title
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Some other course title',
            'description': 'Some course description',
            'is_free': True
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 201
    assert Course.objects.count() == 3


def test_unauthorized_course_creation(test_user, access_token):
    '''
    Test for non-admin users being prevented from creating courses
    '''

    client = APIClient()

    user1 = test_user()

    # Fail - no JWT is provided in header
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Some course title',
            'description': 'Some course description',
            'price': 3.99
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Invalid login or inactive account'
    assert Course.objects.count() == 0

    # Fail - token in header is for non-admin user
    user1.is_staff = False
    user1.save()
    token = access_token(user1, 60)
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Some course title',
            'description': 'Some course description',
            'price': 3.99
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.data['detail'] == 'Admin privileges required for this action'
    assert api_response.status_code == 403
    assert Course.objects.count() == 0

    # Fail - expired token
    token = access_token(user1, 1)
    # Sleep for 2sec
    time.sleep(2)
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Another course title',
            'description': 'Some course description',
            'price': 3.99
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.data['detail'] == 'Must be logged in for this action'
    assert api_response.status_code == 403


def test_bad_course_data_failure(test_user, access_token):
    '''
    Tests for course creation failure due to missing data
    '''

    client = APIClient()

    user1 = test_user()
    user1.is_staff = True
    user1.save()

    token = access_token(user1, 60)

    # Fail - title missing
    api_response = client.post(
        '/api/courses/new-course',
        {
            'description': 'Some course description',
            'price': 3.99
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.data['detail'] == 'Course title is required'
    assert api_response.status_code == 400
    assert Course.objects.count() == 0

    # Fail - description missing
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Another course title',
            'price': 3.99
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.data['detail'] == 'Course description is required'
    assert api_response.status_code == 400
    assert Course.objects.count() == 0

    # Fail - price missing
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Another course title',
            'description': 'Some course description',
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.data['detail'] == 'Course price is required'
    assert api_response.status_code == 400
    assert Course.objects.count() == 0

    # Fail - price is 0.00 but course is not free
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Another course title',
            'description': 'Some course description',
            'price': 0.00
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.data['detail'] == 'Course price is required'
    assert api_response.status_code == 400
    assert Course.objects.count() == 0


def test_duplicate_course_title_failure(test_user, access_token):
    '''
    Tests for course creation failure due to duplicate title
    '''

    client = APIClient()

    user1 = test_user()
    user1.is_staff = True
    user1.save()

    Course.objects.create(
        title='Some course title',
        description='Some course description',
        is_free=True
    )

    token = access_token(user1, 60)

    # Fail - duplicate title
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Some course title',
            'description': 'Some course description',
            'price': 3.99
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.data['detail'] == 'A course with this title already exists'
    assert api_response.status_code == 400
    assert Course.objects.count() == 1
