import pytest
import time
from rest_framework.test import APIClient

from courses.models import Course
from user_auth.tests.fixtures import test_user, access_token
from .fixtures import sample_course

pytestmark = pytest.mark.django_db


def test_course_update_endpoint(
    test_user,
    access_token,
    sample_course
):
    '''Test that course can be updated with PUT request'''

    client = APIClient()

    course1 = sample_course()
    course1.is_draft = False
    course1.save()

    # Admin user
    user1 = test_user()
    user1.is_staff = True
    user1.save()

    # Adding user as instructor of the course
    course1.add_instructor(user1)

    token = access_token(user1, 60)

    # Success
    api_response = client.patch(
        f'/api/courses/{course1.slug}',
        {
            'subtitle': 'This is a test subtitle',
            'price': '15.99'
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert api_response.data['subtitle'] == 'This is a test subtitle'
    assert api_response.data['price'] == '15.99'
    assert api_response.data['is_free'] == False

    # Create second admin user
    user2 = test_user(
        'otheruser@gmail.com',
        'otherpassword',
        is_staff=True
    )
    token = access_token(user2, 60)

    # Make second user course instructor
    course1.add_instructor(user2)

    # Success
    api_response = client.patch(
        f'/api/courses/{course1.slug}',
        {
            'subtitle': 'This is another test subtitle',
            'is_free': 'True'
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert api_response.data['subtitle'] == 'This is another test subtitle'
    assert api_response.data['price'] == '0.00'
    assert api_response.data['is_free'] == True


def test_unauthorized_course_update(
    test_user,
    access_token,
    sample_course
):
    '''Test that only one of the instructors of a course can perform an update'''

    client = APIClient()

    # Fail - Course in draft mode and no admin authenticated
    course1 = sample_course()
    api_response = client.patch(
        f'/api/courses/{course1.slug}',
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
        f'/api/courses/{course1.slug}',
        {
            'subtitle': 'This is a test subtitle',
            'is_free': 'True'
        },
        format='json'
    )
    assert api_response.status_code == 403

    # Fail - user is admin but not instructor
    user1 = test_user()
    user1.is_staff = True
    user1.save()
    token = access_token(user1, 60)

    api_response = client.patch(
        f'/api/courses/{course1.slug}',
        {
            'subtitle': 'This is a test subtitle',
            'is_free': 'True'
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Only an instructor of a course can update a course'

    # Fail - using wrong course URL should give 404
    api_response = client.patch(
        f'/api/courses/{course1.slug+"1"}',
        {
            'subtitle': 'This is a test subtitle',
            'price': '15.99'
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'Course not found from URL'


def test_course_update_bad_data(
    test_user,
    access_token,
    sample_course
):
    '''Test for when an update can be refused due to bad data'''

    client = APIClient()

    course1 = sample_course()

    # Admin user
    user1 = test_user()
    user1.is_staff = True
    user1.save()
    token = access_token(user1, 60)

    # Adding user as instructor of the course
    course1.add_instructor(user1)

    # Fail - course is not free but price is zero
    api_response = client.patch(
        f'/api/courses/{course1.slug}',
        {
            'subtitle': 'This is a test subtitle',
            'price': '0.0',
            'is_free': 'False'
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'Price of a non-free course is required.'

    # Create another course
    course2 = sample_course(index=2)

    # Fail - duplicate course violation
    api_response = client.patch(
        f'/api/courses/{course1.slug}',
        {
            'title': course2.title.lower(),
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'A course with this title already exists'
