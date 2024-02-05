import pytest
import json
from rest_framework.test import APIClient

from courses.models import Course
from lectures.models import Lecture
from registration.models import CourseStudentRegistration
from user_auth.tests.fixtures import test_user, access_token

pytestmark = pytest.mark.django_db


def test_fetch_lecture_list(test_user, access_token):
    '''List view test for lectures'''

    client = APIClient()

    # Create sample course
    course1 = Course.objects.create(
        title='Course 1',
        description='Decr 1',
        is_free=True
    )

    # Create lectures for the course
    lecture1 = Lecture.objects.create(title='Lec 1', course=course1)
    lecture2 = Lecture.objects.create(title='Lec 2', course=course1)
    lecture3 = Lecture.objects.create(title='Lec 3', course=course1)
    lecture4 = Lecture.objects.create(title='Lec 4', course=course1)

    # Fail - as unpublished course lecture should not be listed
    api_response = client.get(
        '/api/courses/{}/lectures/'.format(course1.slug),
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'Course not found'

    # Publish the course
    course1.is_draft = False
    course1.save()

    # Success - no credentials for fetching lecture list
    api_response = client.get(
        '/api/courses/{}/lectures/'.format(course1.slug),
        format='json'
    )
    assert api_response.status_code == 200
    api_response.render()
    api_response.data = json.loads(api_response.content)
    assert len(api_response.data) == 4

    # Create sample user
    user1 = test_user()
    token1 = access_token(user1, 60)

    # Unpublish the course
    course1.is_draft = True
    course1.save()

    # Fail - non-admin user cannot access unpublished lectures
    api_response = client.get(
        '/api/courses/{}/lectures/'.format(course1.slug),
        headers={
            'Authorization': 'Bearer {}'.format(token1)
        },
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'Course not found'

    # Making user admin
    user1.is_staff = True
    user1.save()

    # Admin can fetch lectures of unpublished courses
    api_response = client.get(
        '/api/courses/{}/lectures/'.format(course1.slug),
        headers={
            'Authorization': 'Bearer {}'.format(token1)
        },
        format='json'
    )
    assert api_response.status_code == 200
    api_response.render()
    api_response.data = json.loads(api_response.content)
    assert len(api_response.data) == 4


def test_fetch_lecture(test_user, access_token):
    '''Detail view test for lecture'''

    client = APIClient()

    # Create sample course
    course1 = Course.objects.create(
        title='Course 1',
        description='Decr 1',
        is_free=True
    )

    # Create lectures for the course
    lecture1 = Lecture.objects.create(title='Lec 1', course=course1)
    lecture2 = Lecture.objects.create(title='Lec 2', course=course1)

    # Fail - as unpublished course lecture should not be listed
    api_response = client.get(
        '/api/courses/{slug}/lectures/{id}'.format(
            slug=course1.slug,
            id=lecture1.id
        ),
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'Course not found'

    api_response = client.get(
        '/api/courses/{slug}/lectures/{id}'.format(
            slug=course1.slug,
            id=lecture2.id
        ),
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'Course not found'

    # Publish the course
    course1.is_draft = False
    course1.save()

    # Fail - without credentials lecture details should not listed
    api_response = client.get(
        '/api/courses/{slug}/lectures/{id}'.format(
            slug=course1.slug,
            id=lecture1.id
        ),
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Must be logged in to access a lecture'

    api_response = client.get(
        '/api/courses/{slug}/lectures/{id}'.format(
            slug=course1.slug,
            id=lecture2.id
        ),
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Must be logged in to access a lecture'

    # Create sample user
    user1 = test_user()
    user1.is_active = True
    user1.save()
    token1 = access_token(user1, 60)

    # Fail - unregistered student cannot access lecture details
    api_response = client.get(
        '/api/courses/{slug}/lectures/{id}'.format(
            slug=course1.slug,
            id=lecture1.id
        ),
        headers={
            'Authorization': 'Bearer {}'.format(token1)
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Must register for the course to access a lecture'

    # Register student for course
    CourseStudentRegistration.objects.register_student(user1, course1)

    # Success
    api_response = client.get(
        '/api/courses/{slug}/lectures/{id}'.format(
            slug=course1.slug,
            id=lecture1.id
        ),
        headers={
            'Authorization': 'Bearer {}'.format(token1)
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert api_response.data['title'] == lecture1.title

    # Unpublish the course
    course1.is_draft = True
    course1.save()

    api_response = client.get(
        '/api/courses/{slug}/lectures/{id}'.format(
            slug=course1.slug,
            id=lecture1.id
        ),
        headers={
            'Authorization': 'Bearer {}'.format(token1)
        },
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'Course not found'

    # Make user admin
    user1.is_staff = True
    user1.save()

    api_response = client.get(
        '/api/courses/{slug}/lectures/{id}'.format(
            slug=course1.slug,
            id=lecture2.id
        ),
        headers={
            'Authorization': 'Bearer {}'.format(token1)
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert api_response.data['title'] == lecture2.title
