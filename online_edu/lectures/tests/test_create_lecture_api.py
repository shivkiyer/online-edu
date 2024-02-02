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
    course1 = sample_course

    client = APIClient()

    # Fail - no credentials
    api_response = client.post(
        '/api/courses/{}/lectures/new-lecture'.format(course1.slug),
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
        '/api/courses/{}/lectures/new-lecture'.format(course1.slug),
        {
            'title': 'Some title'
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
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
        '/api/courses/{}/lectures/new-lecture'.format(course1.slug),
        {
            'title': 'Some title'
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Must be an instructor of the course to create lectures'

    # Make user instructor
    course1.add_instructor(user1)

    # Success
    api_response = client.post(
        '/api/courses/{}/lectures/new-lecture'.format(course1.slug),
        {
            'title': 'Some title'
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert Lecture.objects.all().count() == 1
    assert Lecture.objects.all()[0].course.id == course1.id

    # Fail - missing title
    api_response = client.post(
        '/api/courses/{}/lectures/new-lecture'.format(course1.slug),
        {
            'description': 'Some description'
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'The title of a lecture is required'

    # Fail - wrong course slug
    api_response = client.post(
        '/api/courses/{}/lectures/new-lecture'.format(course1.slug+'1'),
        {
            'title': 'Some title'
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'Course not found'

    # Fail - duplicate lecture title within same course
    api_response = client.post(
        '/api/courses/{}/lectures/new-lecture'.format(course1.slug),
        {
            'title': 'Some title'
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'Lecture with the same title exists in the course'

    # Create a second course
    course2 = Course.objects.create(
        title='Some title',
        description='Some descr',
        is_free=True
    )
    course2.add_instructor(user1)

    # Success - lecture with same title in second course
    api_response = client.post(
        '/api/courses/{}/lectures/new-lecture'.format(course2.slug),
        {
            'title': 'Some title'
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert Lecture.objects.all().count() == 2
    assert Lecture.objects.all()[0].course.id == course1.id
    assert Lecture.objects.all()[1].course.id == course2.id
