from django.db import transaction
import pytest

from courses.models import Course
from user_auth.tests.fixtures import test_user

pytestmark = pytest.mark.django_db


def test_course_creation():
    '''Test basic course creation'''

    # Success
    Course.objects.create(
        title='Some course title',
        description='Some course description',
        price=1.99
    )
    assert Course.objects.count() == 1
    course1 = Course.objects.all()[0]
    assert course1.slug != None
    assert course1.is_free == False
    assert course1.is_draft == True
    assert course1.is_archived == False

    # Another success - no description
    Course.objects.create(
        title='Another course title',
        price=2.99
    )
    assert Course.objects.count() == 2

    # Another success - free course
    course2 = Course.objects.create(
        title='Try Another course title',
        is_free=True
    )
    assert course2.price == 0.00
    assert Course.objects.count() == 3


def test_course_bad_data():
    '''
    Test course creation failure due to bad data
    '''

    # Fail - price for a non-free course is 0
    with pytest.raises(Exception):
        with transaction.atomic():
            Course.objects.create(
                title='Some course title',
                description='Some course description',
                price=0.00
            )
    assert Course.objects.count() == 0


def test_course_duplicate_title():
    '''
    Test course creation failure due to duplicate title
    '''

    Course.objects.create(
        title='Some course title',
        description='Some course description',
        price=1.99
    )
    assert Course.objects.count() == 1

    # Fail - Non-unique title
    with pytest.raises(Exception):
        with transaction.atomic():
            Course.objects.create(
                title='Some course title',
                description='Some course description',
                price=1.99
            )
    assert Course.objects.count() == 1


def test_course_instructor(test_user):
    '''
    Test that course instructor must be admin user
    '''

    course1 = Course.objects.create(
        title='Some course title',
        description='Some course description',
        price=1.99
    )

    user1 = test_user()

    # Fail - user is not admin
    user1.is_staff = False
    user1.save()
    with pytest.raises(Exception):
        course1.add_instructor(user1)

    # Make user admin
    user1.is_staff = True
    user1.save()
    course1.add_instructor(user1)
    instructor1 = course1.instructors.all()[0]
    assert instructor1.username == user1.username
