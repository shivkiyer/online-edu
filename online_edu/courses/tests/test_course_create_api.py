import pytest
import time
from rest_framework.test import APIClient

from user_auth.tests.fixtures import test_user, access_token
from courses.models import Course

pytestmark = pytest.mark.django_db


def test_course_create_endpoint(test_user, access_token):
    '''Tests for creating new course'''

    client = APIClient()

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
    assert api_response.data == 'Must be logged in as administrator to create a course'
    assert Course.objects.count() == 0

    # Fail - token in header is for non-admin user
    test_user.is_staff = False
    test_user.save()
    token = access_token(test_user, 15)
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Some course title',
            'description': 'Some course description',
            'price': 3.99
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.data == 'Must be logged in as administrator to create a course'
    assert api_response.status_code == 403
    assert Course.objects.count() == 0

    # Success - token in header is for admin user
    test_user.is_staff = True
    test_user.save()
    token = access_token(test_user, 60)
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Some course title',
            'description': 'Some course description',
            'price': 3.99
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 201
    assert Course.objects.count() == 1

    # Fail - duplicate title
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Some course title',
            'description': 'Some course description',
            'price': 3.99
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.data == 'A course with this title already exists'
    assert api_response.status_code == 400
    assert Course.objects.count() == 1

    # Fail - title missing
    api_response = client.post(
        '/api/courses/new-course',
        {
            'description': 'Some course description',
            'price': 3.99
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.data == 'Course title is required'
    assert api_response.status_code == 400
    assert Course.objects.count() == 1

    # Fail - description missing
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Another course title',
            'price': 3.99
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.data == 'Course description is required'
    assert api_response.status_code == 400
    assert Course.objects.count() == 1

    # Fail - price missing
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Another course title',
            'description': 'Some course description',
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.data == 'Course price is required'
    assert api_response.status_code == 400
    assert Course.objects.count() == 1

    # Fail - price is 0.00 but course is not free
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Another course title',
            'description': 'Some course description',
            'price': 0.00
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.data == 'Course price is required'
    assert api_response.status_code == 400
    assert Course.objects.count() == 1

    # Fail - expired token
    token = access_token(test_user, 1)
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
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.data == 'Must be logged in as administrator to create a course'
    assert api_response.status_code == 403
    assert Course.objects.count() == 1

    # Success - another course with correct token
    token = access_token(test_user, 60)
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Another course title',
            'description': 'Some course description',
            'price': 3.99
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 201
    assert Course.objects.count() == 2

    # Success - a free course with correct token
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Some other course title',
            'description': 'Some course description',
            'is_free': True
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 201
    assert Course.objects.count() == 3
