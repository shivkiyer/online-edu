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
    user1.save()

    # Test course
    course1 = sample_course

    # Test lectures
    lectures = test_lectures(course1, 5)

    # Fail - no credentials
    api_response = client.post(
        '/api/courses/{slug}/lectures/{id}/move-lecture/up'.format(
            slug=course1.slug,
            id=lectures[0].id
        ),
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Invalid login or inactive account'

    # Create JWT
    token1 = access_token(user1, 60)

    # Fail - user is non-admin
    api_response = client.post(
        '/api/courses/{slug}/lectures/{id}/move-lecture/up'.format(
            slug=course1.slug,
            id=lectures[0].id
        ),
        headers={
            'Authorization': 'Bearer {}'.format(token1)
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
        '/api/courses/{slug}/lectures/{id}/move-lecture/up'.format(
            slug=course1.slug,
            id=lectures[0].id
        ),
        headers={
            'Authorization': 'Bearer {}'.format(token1)
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Only an instructor can change the order of lectures'

    # Make test user instructor
    course1.add_instructor(user1)

    # Fail - cannot move first lecture up
    api_response = client.post(
        '/api/courses/{slug}/lectures/{id}/move-lecture/up'.format(
            slug=course1.slug,
            id=lectures[0].id
        ),
        headers={
            'Authorization': 'Bearer {}'.format(token1)
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'Lecture is already the first in the course'

    # Fail - cannot move last lecture down
    api_response = client.post(
        '/api/courses/{slug}/lectures/{id}/move-lecture/down'.format(
            slug=course1.slug,
            id=lectures[4].id
        ),
        headers={
            'Authorization': 'Bearer {}'.format(token1)
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'Lecture is already the last in the course'

    # Success - move 2nd lecture up
    api_response = client.post(
        '/api/courses/{slug}/lectures/{id}/move-lecture/up'.format(
            slug=course1.slug,
            id=lectures[1].id
        ),
        headers={
            'Authorization': 'Bearer {}'.format(token1)
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
        '/api/courses/{slug}/lectures/{id}/move-lecture/up'.format(
            slug=course1.slug,
            id=lectures[3].id
        ),
        headers={
            'Authorization': 'Bearer {}'.format(token1)
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
        '/api/courses/{slug}/lectures/{id}/move-lecture/up'.format(
            slug=course1.slug,
            id=lectures[3].id
        ),
        headers={
            'Authorization': 'Bearer {}'.format(token1)
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
        '/api/courses/{slug}/lectures/{id}/move-lecture/up'.format(
            slug=course1.slug,
            id=lectures[3].id
        ),
        headers={
            'Authorization': 'Bearer {}'.format(token1)
        },
        format='json'
    )
    assert api_response.status_code == 200
    check_lectures = Lecture.objects.all()
    assert check_lectures[0].title == lectures[3].title
    assert check_lectures[1].title == lectures[1].title
    assert check_lectures[2].title == lectures[0].title
    assert check_lectures[3].title == lectures[2].title

    # Sequence now is 3-1-0-2-4
    # Fail - 3rd lecture is now the first
    api_response = client.post(
        '/api/courses/{slug}/lectures/{id}/move-lecture/up'.format(
            slug=course1.slug,
            id=lectures[3].id
        ),
        headers={
            'Authorization': 'Bearer {}'.format(token1)
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'Lecture is already the first in the course'

    # Success
    api_response = client.post(
        '/api/courses/{slug}/lectures/{id}/move-lecture/down'.format(
            slug=course1.slug,
            id=lectures[0].id
        ),
        headers={
            'Authorization': 'Bearer {}'.format(token1)
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
        '/api/courses/{slug}/lectures/{id}/move-lecture/down'.format(
            slug=course1.slug,
            id=lectures[0].id
        ),
        headers={
            'Authorization': 'Bearer {}'.format(token1)
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

    # Fail - lecture 0 is already the last
    api_response = client.post(
        '/api/courses/{slug}/lectures/{id}/move-lecture/down'.format(
            slug=course1.slug,
            id=lectures[0].id
        ),
        headers={
            'Authorization': 'Bearer {}'.format(token1)
        },
        format='json'
    )
    assert api_response.status_code == 400
    assert api_response.data['detail'] == 'Lecture is already the last in the course'
