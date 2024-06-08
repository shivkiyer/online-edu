import pytest
from rest_framework.test import APIClient

from lectures.models import Lecture
from user_auth.tests.fixtures import test_user, access_token
from courses.tests.fixtures import sample_course
from fixtures import test_lectures

pytestmark = pytest.mark.django_db


def test_moving_lecture_endpoint(
    test_user,
    access_token,
    sample_course,
    test_lectures
):
    '''Test that lectures are moved in the course lecture list'''

    client = APIClient()

    # Test user
    user1 = test_user()
    user1.is_active = True
    user1.is_staff = True
    user1.save()

    # Test course
    course1 = sample_course

    # Make test user instructor
    course1.add_instructor(user1)

    # Test lectures
    lectures = test_lectures(course1, 5)

    # Create JWT
    token1 = access_token(user1, 60)

    # Success - move 2nd lecture up
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/{lectures[1].id}/move-lecture/up',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 200
    check_lectures = Lecture.objects.all()
    assert check_lectures[0].title == lectures[1].title
    assert check_lectures[1].title == lectures[0].title

    # Sequence now is 1-0-2-3-4
    # Success
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/{lectures[3].id}/move-lecture/up',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 200
    check_lectures = Lecture.objects.all()
    assert check_lectures[0].title == lectures[1].title
    assert check_lectures[1].title == lectures[0].title
    assert check_lectures[2].title == lectures[3].title
    assert check_lectures[3].title == lectures[2].title

    # Sequence now is 1-0-3-2-4
    # Success
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/{lectures[3].id}/move-lecture/up',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 200
    check_lectures = Lecture.objects.all()
    assert check_lectures[0].title == lectures[1].title
    assert check_lectures[1].title == lectures[3].title
    assert check_lectures[2].title == lectures[0].title
    assert check_lectures[3].title == lectures[2].title

    # Sequence now is 1-3-0-2-4
    # Success
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/{lectures[3].id}/move-lecture/up',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 200
    check_lectures = Lecture.objects.all()
    assert check_lectures[0].title == lectures[3].title
    assert check_lectures[1].title == lectures[1].title
    assert check_lectures[2].title == lectures[0].title
    assert check_lectures[3].title == lectures[2].title

    # Success
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/{lectures[0].id}/move-lecture/down',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 200
    check_lectures = Lecture.objects.all()
    assert check_lectures[0].title == lectures[3].title
    assert check_lectures[1].title == lectures[1].title
    assert check_lectures[2].title == lectures[2].title
    assert check_lectures[3].title == lectures[0].title
    assert check_lectures[4].title == lectures[4].title

    # Sequence now is 3-1-2-0-4
    # Success
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/{lectures[0].id}/move-lecture/down',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 200
    check_lectures = Lecture.objects.all()
    assert check_lectures[0].title == lectures[3].title
    assert check_lectures[1].title == lectures[1].title
    assert check_lectures[2].title == lectures[2].title
    assert check_lectures[3].title == lectures[4].title
    assert check_lectures[4].title == lectures[0].title


def test_unauthorized_moving_lecture(
    test_user,
    access_token,
    sample_course,
    test_lectures
):
    '''Test that lectures can be moved only by instructors'''

    client = APIClient()

    # Test user
    user1 = test_user()
    user1.is_active = True
    user1.save()

    # Test course
    course1 = sample_course

    # Test lectures
    lectures = test_lectures(course1, 5)

    # Fail - no credentials
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/{lectures[0].id}/move-lecture/up',
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Invalid login or inactive account'

    # Create JWT
    token1 = access_token(user1, 60)

    # Fail - user is non-admin
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/{lectures[0].id}/move-lecture/up',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Admin privileges required for this action'

    # Make test user admin
    user1.is_staff = True
    user1.save()

    # Fail - user is not instructor
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/{lectures[0].id}/move-lecture/up',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Only an instructor can change the order of lectures'


def test_moving_extreme_lectures(
    test_user,
    access_token,
    sample_course,
    test_lectures
):
    '''Test that lectures are moved in the course lecture list'''

    client = APIClient()

    # Test user
    user1 = test_user()
    user1.is_active = True
    user1.is_staff = True
    user1.save()

    # Test course
    course1 = sample_course

    # Make test user instructor
    course1.add_instructor(user1)

    # Create JWT
    token1 = access_token(user1, 60)

    # Test lectures
    lectures = test_lectures(course1, 5)

    # Fail - cannot move first lecture up
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/{lectures[0].id}/move-lecture/up',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'Lecture is already the first in the course'

    # Fail - cannot move last lecture down
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/{lectures[4].id}/move-lecture/down',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'Lecture is already the last in the course'


def test_moving_lecture_bad_data(
    test_user,
    access_token,
    sample_course,
    test_lectures
):
    '''Test that lectures are moved according to correct input directions'''

    client = APIClient()

    # Test user
    user1 = test_user()
    user1.is_active = True
    user1.is_staff = True
    user1.save()

    # Test course
    course1 = sample_course

    # Make test user instructor
    course1.add_instructor(user1)

    # Create JWT
    token1 = access_token(user1, 60)

    # Test lectures
    lectures = test_lectures(course1, 5)

    # Fail - wrong direction
    api_response = client.post(
        f'/api/courses/{course1.slug}/lectures/{lectures[2].id}/move-lecture/downn',
        headers={
            'Authorization': f'Bearer {token1}'
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'Direction in which the lecture needs to be moved can be up or down'
