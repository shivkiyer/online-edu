import pytest
from rest_framework.test import APIClient

from user_auth.tests.fixtures import test_user, access_token
from courses.tests.fixtures import sample_course

pytestmark = pytest.mark.django_db


def test_add_instructor(sample_course, test_user, access_token):
    '''Test endpoint for adding an instructor to the course'''

    client = APIClient()

    # Creating course with one instructor
    course1 = sample_course
    user1 = test_user(
        'someuser@gmail.com',
        'somepassword',
        True
    )
    user1.is_active = True
    user1.save()
    course1.add_instructor(user1)

    # Create second user - not admin, not active
    user2 = test_user(
        'otheruser@gmail.com',
        'somepassword',
        False
    )

    token = access_token(user1, 60)

    # Fail - no JWT token in header
    api_response = client.post(
        '/api/registration/{}/add-instructor'.format(course1.slug),
        {
            'email': user2.username
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Invalid login or inactive account'

    # Fail - new instructor not admin
    api_response = client.post(
        '/api/registration/{}/add-instructor'.format(course1.slug),
        {
            'email': user2.username
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Instructors have to be administrators'

    user2.is_staff = True
    user2.save()

    # Fail - wrong course url
    api_response = client.post(
        '/api/registration/{}/add-instructor'.format(course1.slug+'1'),
        {
            'email': user2.username
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'Course not found from URL'

    # Success - instructor added
    api_response = client.post(
        '/api/registration/{}/add-instructor'.format(course1.slug),
        {
            'email': user2.username
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 200

    # Fail - adding user who is already instructor
    api_response = client.post(
        '/api/registration/{}/add-instructor'.format(course1.slug),
        {
            'email': user2.username
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'Already an instructor'

    # Fail - adding non-existing user
    api_response = client.post(
        '/api/registration/{}/add-instructor'.format(course1.slug),
        {
            'email': 'randomuser@gmail.com'
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'User not found'

    user1.is_active = False
    user1.save()

    # Fail - requesting instructor has inactive account
    api_response = client.post(
        '/api/registration/{}/add-instructor'.format(course1.slug),
        {
            'email': user2.username
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Must be logged in for this action'

    # Delete requesting user
    user1.delete()

    # Fail - requesting user does not exist
    api_response = client.post(
        '/api/registration/{}/add-instructor'.format(course1.slug),
        {
            'email': user2.username
        },
        headers={
            'Authorization': 'Bearer {}'.format(token)
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Must be logged in for this action'
