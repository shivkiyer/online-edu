import pytest
import time
from rest_framework.test import APIClient

from courses.models import Course
from user_auth.tests.fixtures import test_user, access_token, test_configurable_user
from .fixtures import sample_course

pytestmark = pytest.mark.django_db


def test_only_instructor_can_update_course(
        test_user,
        access_token,
        test_configurable_user,
        sample_course
):
    '''Test that only one of the instructors of a course can perform an update'''

    client = APIClient()

    # Fail - Course in draft mode and no admin authenticated
    course1 = sample_course
    api_response = client.patch(
        '/api/courses/{}'.format(course1.slug),
        {
            'subtitle': 'This is a test subtitle',
            'is_free': 'True'
        },
        format='json'
    )
    assert api_response.status_code == 403

    # Fail - Setting the course as not draft
    course1.is_draft = False
    course1.save()

    api_response = client.patch(
        '/api/courses/{}'.format(course1.slug),
        {
            'subtitle': 'This is a test subtitle',
            'is_free': 'True'
        },
        format='json'
    )
    assert api_response.status_code == 403

    # Fail - user is admin but not instructor
    user1 = test_user
    user1.is_staff = True
    user1.save()
    token = access_token(user1, 60)

    api_response = client.patch(
        '/api/courses/{}'.format(course1.slug),
        {
            'subtitle': 'This is a test subtitle',
            'is_free': 'True'
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data == 'Only an instructor of a course can update a course'

    # Adding user as instructor of the course
    course1.add_instructor(user1)

    # Fail - using wrong course URL should give 404
    api_response = client.patch(
        '/api/courses/{}'.format(course1.slug+"1"),
        {
            'subtitle': 'This is a test subtitle',
            'price': '15.99'
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data == 'Course not found from URL'

    # Success - user is instructor for course
    api_response = client.patch(
        '/api/courses/{}'.format(course1.slug),
        {
            'subtitle': 'This is a test subtitle',
            'price': '15.99'
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert api_response.data['subtitle'] == 'This is a test subtitle'
    assert api_response.data['price'] == '15.99'
    assert api_response.data['is_free'] == False

    # Fail - send request as another admin user but not instructor
    user2 = test_configurable_user(
        'otheruser@gmail.com', 'otherpassword', is_staff=True)
    token = access_token(user2, 60)
    api_response = client.patch(
        '/api/courses/{}'.format(course1.slug),
        {
            'subtitle': 'This is another test subtitle',
            'is_free': 'True'
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data == 'Only an instructor of a course can update a course'

    # Success - add this admin user as course instructor
    course1.add_instructor(user2)
    api_response = client.patch(
        '/api/courses/{}'.format(course1.slug),
        {
            'subtitle': 'This is another test subtitle',
            'is_free': 'True'
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert api_response.data['subtitle'] == 'This is another test subtitle'
    assert api_response.data['price'] == '0.00'
    assert api_response.data['is_free'] == True
