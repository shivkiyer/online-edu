import pytest
from rest_framework.test import APIClient

from courses.models import Course
from courses.tests.fixtures import sample_course
from user_auth.tests.fixtures import test_user, access_token
from lectures.models import Lecture

pytestmark = pytest.mark.django_db


def test_create_lecture_endpoint(
    test_user,
    sample_course,
    access_token
):
    '''Test for creating new lecture'''

    # Create test user and course
    user1 = test_user()
    # Make user admin
    user1.is_staff = True
    user1.save()

    course1 = sample_course()

    # Make user instructor
    course1.add_instructor(user1)

    token = access_token(user1, 60)

    client = APIClient()

    # Success
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/new-lecture',
        {
            'title': 'Some title'
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert Lecture.objects.all().count() == 1
    assert Lecture.objects.all()[0].course.id == course1.id

    # Create a second course
    course2 = sample_course(index=2)
    course2.add_instructor(user1)

    # Success - lecture with same title in second course
    api_response = client.post(
        f'/api/courses/{course2.slug}/lectures/new-lecture',
        {
            'title': 'Some title'
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert Lecture.objects.all().count() == 2
    assert Lecture.objects.all()[0].course.id == course1.id
    assert Lecture.objects.all()[1].course.id == course2.id


def test_unauthorized_lecture_creation(
    test_user,
    sample_course,
    access_token
):
    '''Test to verify that only a course instructor can create lectures'''

    # Create test user and course
    user1 = test_user()
    course1 = sample_course()

    client = APIClient()

    # Fail - no credentials
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/new-lecture',
        {
            'title': 'Some title'
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Invalid login or inactive account'

    # Fail - non-admin credentials
    token = access_token(user1, 60)
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/new-lecture',
        {
            'title': 'Some title'
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Admin privileges required for this action'

    # Make user admin
    user1.is_staff = True
    user1.save()

    # Fail -  user is not instructor of course
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/new-lecture',
        {
            'title': 'Some title'
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Must be an instructor of the course to create or update lectures'


def test_create_lecture_bad_data(
    test_user,
    sample_course,
    access_token
):
    '''Test for bad data used for creating lecture'''

    # Create test user and course
    user1 = test_user()
    user1.is_staff = True
    user1.save()

    course1 = sample_course()
    # Make user instructor
    course1.add_instructor(user1)

    token = access_token(user1, 60)

    client = APIClient()

    # Fail - missing title
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/new-lecture',
        {
            'description': 'Some description'
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'The title of a lecture is required'

    # Fail - wrong course slug
    api_response = client.post(
        f'/api/courses/{course1.slug+"1"}/lectures/new-lecture',
        {
            'title': 'Some title'
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'Course not found'

    Lecture.objects.create(
        course=course1,
        title='Some title'
    )

    # Fail - duplicate lecture title within same course
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/new-lecture',
        {
            'title': 'Some title'
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'Lecture with the same title exists in the course'
