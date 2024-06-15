import pytest
from rest_framework.test import APIClient

from user_auth.tests.fixtures import test_user, access_token
from courses.tests.fixtures import sample_course

pytestmark = pytest.mark.django_db


def test_add_instructor(sample_course, test_user, access_token):
    '''Test endpoint for adding an instructor to the course'''

    client = APIClient()

    # Creating course with one instructor
    course1 = sample_course()
    user1 = test_user(
        'someuser@gmail.com',
        'somepassword',
        True
    )
    user1.is_active = True
    user1.save()
    course1.add_instructor(user1)

    token = access_token(user1, 60)

    # Create second user - not admin, not active
    user2 = test_user(
        'otheruser@gmail.com',
        'somepassword',
        False
    )
    user2.is_staff = True
    user2.save()

    # Success - instructor added
    api_response = client.post(
        f'/api/registration/{course1.slug}/add-instructor',
        {
            'email': user2.username
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 200


def test_unauthorized_instructor_addition(sample_course, test_user, access_token):
    '''That that only an instructor can add another admin as instructor'''

    client = APIClient()

    # Creating course with one instructor
    course1 = sample_course()
    user1 = test_user(
        'someuser@gmail.com',
        'somepassword'
    )
    user1.is_active = True
    user1.save()

    token = access_token(user1, 60)

    # Create second user - not admin, not active
    user2 = test_user(
        'otheruser@gmail.com',
        'somepassword',
        False
    )

    # Fail - no JWT token in header
    api_response = client.post(
        f'/api/registration/{course1.slug}/add-instructor',
        {
            'email': user2.username
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Invalid login or inactive account'

    # Fail - requesting user not admin or instructor
    api_response = client.post(
        f'/api/registration/{course1.slug}/add-instructor',
        {
            'email': user2.username
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Admin privileges required for this action'

    user1.is_staff = True
    user1.save()

    # Fail - requesting user not instructor
    api_response = client.post(
        f'/api/registration/{course1.slug}/add-instructor',
        {
            'email': user2.username
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Must be logged in as an instructor'

    course1.add_instructor(user1)

    # Fail - new user not admin
    api_response = client.post(
        f'/api/registration/{course1.slug}/add-instructor',
        {
            'email': user2.username
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Instructors have to be administrators'

    user1.is_active = False
    user1.save()

    # Fail - requesting instructor has inactive account
    api_response = client.post(
        f'/api/registration/{course1.slug}/add-instructor',
        {
            'email': user2.username
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Must be logged in for this action'

    # Delete requesting user
    user1.delete()

    # Fail - requesting user does not exist
    api_response = client.post(
        f'/api/registration/{course1.slug}/add-instructor',
        {
            'email': user2.username
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Must be logged in for this action'


def test_add_invalid_instructor(sample_course, test_user, access_token):
    '''
    Test that instructor have to be registered users and 
    not already instuctors in the course.
    '''

    client = APIClient()

    # Creating course with one instructor
    course1 = sample_course()
    user1 = test_user(
        'someuser@gmail.com',
        'somepassword',
        True
    )
    user1.is_active = True
    user1.save()
    course1.add_instructor(user1)

    # Create second admin user
    user2 = test_user(
        'otheruser@gmail.com',
        'somepassword',
        True
    )

    token = access_token(user1, 60)

    # Fail - adding non-existing user
    api_response = client.post(
        f'/api/registration/{course1.slug}/add-instructor',
        {
            'email': 'randomuser@gmail.com'
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'User not found'

    course1.add_instructor(user2)

    # Fail - adding user who is already instructor
    api_response = client.post(
        f'/api/registration/{course1.slug}/add-instructor',
        {
            'email': user2.username
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'Already an instructor'

    user1.is_active = False
    user1.save()


def test_add_instructor_to_course_not_found(sample_course, test_user, access_token):
    '''Test that instructor cannot be added to non-existing courses.'''

    client = APIClient()

    # Creating course with one instructor
    course1 = sample_course()
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
        True
    )
    user2.is_staff = True
    user2.save()

    token = access_token(user1, 60)

    # Fail - wrong course url
    api_response = client.post(
        f'/api/registration/{course1.slug+"1"}/add-instructor',
        {
            'email': user2.username
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'Course not found from URL'
