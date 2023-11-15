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
    assert course1.is_published == False
    assert course1.is_archived == False

    # Fail - Non-unique title
    with pytest.raises(Exception):
        with transaction.atomic():
            Course.objects.create(
                title='Some course title',
                description='Some course description',
                price=1.99
            )
    assert Course.objects.count() == 1

    # Fail - price for a non-free course is 0
    with pytest.raises(Exception):
        with transaction.atomic():
            Course.objects.create(
                title='Some course title',
                description='Some course description',
                price=0.00
            )
    assert Course.objects.count() == 1

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


def test_course_instructor(test_user):
    '''Test that course instructor must be admin user'''
    course1 = Course.objects.create(
        title='Some course title',
        description='Some course description',
        price=1.99
    )

    # Fail - user is not admin
    test_user.is_staff = False
    test_user.save()
    with pytest.raises(Exception):
        course1.add_instructor(test_user)

    # Make user admin
    test_user.is_staff = True
    test_user.save()
    course1.add_instructor(test_user)
    instructor1 = course1.instructors.all()[0]
    assert instructor1.username == test_user.username
