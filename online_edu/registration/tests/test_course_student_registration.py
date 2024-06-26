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

    user1 = test_user()

    course1 = sample_course()
    course1.is_draft = False
    course1.save()

    client = APIClient()

    # Creating JWT
    token = access_token(user1, 60)

    # Success
    # active user with credentials should be able to register
    api_response = client.post(
        f'/api/registration/{course1.slug}/register-student',
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert len(api_response.data) == 1

    course2 = sample_course(index=2)
    course2.is_draft = False
    course2.save()

    # Success
    # user should be able to register for another course
    api_response = client.post(
        f'/api/registration/{course2.slug}/register-student',
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert len(api_response.data) == 2


def test_register_student_for_course1(
    test_user,
    sample_course,
    access_token
):
    '''Test the endpoint for registering students in courses'''

    user1 = test_user()
    user1.is_active = False
    user1.save()
    course1 = sample_course()

    client = APIClient()

    # Fail
    # credentials needed for registration
    api_response = client.post(
        f'/api/registration/{course1.slug}/register-student',
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Invalid login or inactive account'

    # Creating JWT
    token = access_token(user1, 60)

    # Fail
    # an inactive user should not be able to register
    api_response = client.post(
        f'/api/registration/{course1.slug}/register-student',
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Must be logged in for this action'

    # Activate user
    user1.is_active = True
    user1.save()

    # Fail
    # course must be published for registration
    api_response = client.post(
        f'/api/registration/{course1.slug}/register-student',
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'Course not found from URL'

    # Publishing course
    course1.is_draft = False
    course1.save()

    # Fail - wrong course URL
    api_response = client.post(
        f'/api/registration/{course1.slug+"1"}/register-student',
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'Course not found from URL'

    # Pass
    # active user with credentials should be able to register
    api_response = client.post(
        f'/api/registration/{course1.slug}/register-student',
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert len(api_response.data) == 1

    # Fail
    # user should not be able to register if already registered
    api_response = client.post(
        f'/api/registration/{course1.slug}/register-student',
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'User is already registered'

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
        f'/api/registration/{course2.slug}/register-student',
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 200
    assert len(api_response.data) == 2


def test_unauthorized_registration(
    test_user,
    sample_course,
    access_token
):
    '''Test that only users with active accounts can register'''

    user1 = test_user()
    user1.is_active = False
    user1.save()

    course1 = sample_course()
    course1.is_draft = False
    course1.save()

    client = APIClient()

    # Fail
    # credentials needed for registration
    api_response = client.post(
        f'/api/registration/{course1.slug}/register-student',
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Invalid login or inactive account'

    # Creating JWT
    token = access_token(user1, 60)

    # Fail
    # an inactive user should not be able to register
    api_response = client.post(
        f'/api/registration/{course1.slug}/register-student',
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Must be logged in for this action'


def test_invalid_course_registration(
    test_user,
    sample_course,
    access_token
):
    '''Test that users can only register for published courses'''

    user1 = test_user()

    # Creating JWT
    token = access_token(user1, 60)

    course1 = sample_course()

    client = APIClient()

    # Fail
    # course must be published for registration
    api_response = client.post(
        f'/api/registration/{course1.slug}/register-student',
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'Course not found from URL'

    # Publishing course but archiving it
    course1.is_draft = False
    course1.is_archived = True
    course1.save()

    # Fail
    # course should not be archived
    api_response = client.post(
        f'/api/registration/{course1.slug}/register-student',
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'Course not found from URL'

    # Fail - wrong course URL
    api_response = client.post(
        f'/api/registration/{course1.slug+"1"}/register-student',
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 404
    assert api_response.data['detail'] == 'Course not found from URL'


def test_multiple_registration(
    test_user,
    sample_course,
    access_token
):
    '''Test that users can only register once'''

    user1 = test_user()

    # Creating JWT
    token = access_token(user1, 60)

    course1 = sample_course()
    course1.is_draft = False
    course1.save()

    client = APIClient()

    # Register student for course
    api_response = client.post(
        f'/api/registration/{course1.slug}/register-student',
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )

    # Fail
    # user should not be able to register if already registered
    api_response = client.post(
        f'/api/registration/{course1.slug}/register-student',
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'User is already registered'
