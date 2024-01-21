import pytest
from rest_framework.test import APIClient

from courses.tests.fixtures import sample_course
from user_auth.tests.fixtures import test_user, access_token
from courses.models import Course

pytestmark = pytest.mark.django_db


def test_register_student_for_course(
    test_user,
    sample_course,
    access_token
):
    '''Test the endpoint for registering students in courses'''

    user1 = test_user
    user1.is_active = False
    user1.save()
    course1 = sample_course

    client = APIClient()

    # Fail
    # credentials needed for registration
    api_response = client.post(
        '/api/registration/{}/register-student'.format(course1.slug),
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data == 'Invalid login or inactive account'

    # Creating JWT
    token = access_token(user1, 60)

    # Fail
    # an inactive user should not be able to register
    api_response = client.post(
        '/api/registration/{}/register-student'.format(course1.slug),
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data == 'Must be logged in for this action'

    # Activate user
    user1.is_active = True
    user1.save()

    # Fail
    # course must be published for registration
    api_response = client.post(
        '/api/registration/{}/register-student'.format(course1.slug),
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data == 'Course not found from URL'

    # Publishing course
    course1.is_draft = False
    course1.save()

    # Fail - wrong course URL
    api_response = client.post(
        '/api/registration/{}/register-student'.format(course1.slug+'1'),
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data == 'Course not found from URL'

    # Pass
    # active user with credentials should be able to register
    api_response = client.post(
        '/api/registration/{}/register-student'.format(course1.slug),
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert len(api_response.data) == 1

    # Fail
    # user should not be able to register if already registered
    api_response = client.post(
        '/api/registration/{}/register-student'.format(course1.slug),
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data == 'User is already registered'

    course2 = Course(
        title='Some course',
        description='Some description',
        is_free=True
    )
    course2.is_draft = False
    course2.save()

    # Pass
    # user should be able to register for another course
    api_response = client.post(
        '/api/registration/{}/register-student'.format(course2.slug),
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert len(api_response.data) == 2
