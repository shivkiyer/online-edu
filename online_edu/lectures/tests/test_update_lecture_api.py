import pytest
from rest_framework.test import APIClient

from courses.tests.fixtures import sample_course
from user_auth.tests.fixtures import test_user, access_token
from lectures.models import Lecture

pytestmark = pytest.mark.django_db


def test_update_lecture_endpoint(
    test_user,
    access_token,
    sample_course
):
    '''Test for updating a lecture'''

    client = APIClient()

    # Test user
    user1 = test_user()
    user1.is_active = True
    user1.save()

    # Test course
    course1 = sample_course

    # Test lecture
    lecture1 = Lecture.objects.create(
        title='Lecture 1',
        course=course1
    )

    # Fail - no credentials
    api_response = client.patch(
        '/api/courses/{slug}/lectures/{id}'.format(
            slug=course1.slug,
            id=lecture1.id
        ),
        {
            'title': 'Lecture 1 modified'
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Invalid login or inactive account'

    # Create JWT for test user
    token1 = access_token(user1, 60)

    # Fail - user not admin
    api_response = client.patch(
        '/api/courses/{slug}/lectures/{id}'.format(
            slug=course1.slug,
            id=lecture1.id
        ),
        {
            'title': 'Lecture 1 modified'
        },
        headers={
            'Authorization': 'Bearer {}'.format(token1)
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Admin privileges required for this action'

    # Make user admin
    user1.is_staff = True
    user1.save()

    # Fail - user not instructor of course
    api_response = client.patch(
        '/api/courses/{slug}/lectures/{id}'.format(
            slug=course1.slug,
            id=lecture1.id
        ),
        {
            'title': 'Lecture 1 modified'
        },
        headers={
            'Authorization': 'Bearer {}'.format(token1)
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Must be an instructor of the course to create lectures'

    # Make user instructor
    course1.add_instructor(user1)

    # Success
    api_response = client.patch(
        '/api/courses/{slug}/lectures/{id}'.format(
            slug=course1.slug,
            id=lecture1.id
        ),
        {
            'title': 'Lecture 1 modified'
        },
        headers={
            'Authorization': 'Bearer {}'.format(token1)
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert api_response.data['title'] == 'Lecture 1 modified'
    assert Lecture.objects.all()[0].title == 'Lecture 1 modified'

    # Success - title missing, only updating description
    api_response = client.patch(
        '/api/courses/{slug}/lectures/{id}'.format(
            slug=course1.slug,
            id=lecture1.id
        ),
        {
            'description': 'New description'
        },
        headers={
            'Authorization': 'Bearer {}'.format(token1)
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert api_response.data['title'] == 'Lecture 1 modified'
    assert api_response.data['description'] == 'New description'
    assert Lecture.objects.all()[0].description == 'New description'

    # Fail - title and description missing
    api_response = client.patch(
        '/api/courses/{slug}/lectures/{id}'.format(
            slug=course1.slug,
            id=lecture1.id
        ),
        {},
        headers={
            'Authorization': 'Bearer {}'.format(token1)
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'Empty request body'

    # Create another lecture
    lecture2 = Lecture.objects.create(
        title='Lec 2',
        course=course1
    )

    # Fail - duplicate title for update
    api_response = client.patch(
        '/api/courses/{slug}/lectures/{id}'.format(
            slug=course1.slug,
            id=lecture1.id
        ),
        {
            'title': 'Lec 2'
        },
        headers={
            'Authorization': 'Bearer {}'.format(token1)
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'Lecture with the same title exists in the course'
