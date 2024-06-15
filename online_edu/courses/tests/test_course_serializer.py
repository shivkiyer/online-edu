import pytest
from decimal import Decimal

from courses.models import Course
from courses.serializers import CourseSerializer
from user_auth.tests.fixtures import test_user
from courses.tests.fixtures import sample_course

pytestmark = pytest.mark.django_db


def test_course_serializer_create(test_user):
    '''
    Test CourseSerializer for creating courses
    '''

    user1 = test_user()
    user1.is_staff = True
    user1.save()

    # Success - free course
    serializer = CourseSerializer(data={
        'title': 'Some course title',
        'description': 'Some course description',
        'is_free': 'True'
    })
    course1 = serializer.save(user=user1)
    assert course1.price == 0
    assert course1.is_draft == True
    assert course1.is_archived == False
    assert course1.slug is not None
    assert course1.created_at is not None
    assert course1.updated_at is not None
    assert Course.objects.all().count() == 1

    # Success - non-free course
    serializer = CourseSerializer(data={
        'title': 'Another course title',
        'description': 'Some course description',
        'price': 1.01
    })
    course2 = serializer.save(user=user1)
    assert course2.is_free == False
    assert course2.is_draft == True
    assert course2.is_archived == False
    assert course2.slug is not None
    assert course2.created_at is not None
    assert course2.updated_at is not None
    assert Course.objects.all().count() == 2


def test_unauthorized_course_serializer_create(test_user):
    '''Test CourseSerializer for creating courses'''

    # Non-admin user
    user1 = test_user()

    # Must be created by admin user
    serializer = CourseSerializer(data={
        'title': 'Some course title',
        'description': 'Some course description',
        'is_free': 'True'
    })
    with pytest.raises(Exception) as e:
        serializer.save(user=user1)
    assert str(e.value) == 'Must be logged in as administrator to create a course'

    # Making user admin
    user1.is_staff = True
    user1.save()

    # Success - free course
    serializer = CourseSerializer(data={
        'title': 'Some course title',
        'description': 'Some course description',
        'is_free': 'True'
    })
    course1 = serializer.save(user=user1)
    assert course1.price == 0
    assert course1.is_draft == True
    assert course1.is_archived == False
    assert course1.slug is not None
    assert course1.created_at is not None
    assert course1.updated_at is not None
    assert Course.objects.all().count() == 1


def test_serializer_create_bad_data(test_user):
    '''Test CourseSerializer errors for bad data'''

    user1 = test_user()
    user1.is_staff = True
    user1.save()

    # Missing title
    serializer = CourseSerializer(data={})
    with pytest.raises(Exception) as e:
        serializer.save(user=user1)
    assert str(e.value) == 'Course title is required'

    # Missing description
    serializer = CourseSerializer(data={
        'title': 'Some course title'
    })
    with pytest.raises(Exception) as e:
        serializer.save(user=user1)
    assert str(e.value) == 'Course description is required'

    # Missing price of free info
    serializer = CourseSerializer(data={
        'title': 'Some course title',
        'description': 'Some course description'
    })
    with pytest.raises(Exception) as e:
        serializer.save(user=user1)
    assert str(e.value) == 'Course price is required'


def test_serializer_duplicate_title(test_user, sample_course):
    '''Test CourseSerializer error for duplicate course title'''

    user1 = test_user()
    user1.is_staff = True
    user1.save()

    course1 = sample_course()

    # Duplicate course title
    serializer = CourseSerializer(data={
        'title': course1.title,
        'description': 'Some course description',
        'is_free': 'True'
    })
    with pytest.raises(Exception) as e:
        serializer.save(user=user1)
    assert str(e.value) == 'A course with this title already exists'


def test_course_serializer_update(test_user, sample_course):
    '''Testing CourseSerializer for updating courses'''

    user1 = test_user()
    user1.is_staff = True
    user1.save()

    # Test course
    course1 = sample_course()

    course1.add_instructor(user1)

    # Success - title changed
    serializer = CourseSerializer(
        course1,
        data={'title': 'Changed title'},
        partial=True
    )
    course_obj = serializer.save(user=user1)
    assert course_obj.title == 'Changed title'

    # Success - subtitle and price changed
    serializer = CourseSerializer(
        course1,
        data={
            'subtitle': 'Sample subitle',
            'price': 99.99
        },
        partial=True
    )
    course_obj = serializer.save(user=user1)
    assert course_obj.subtitle == 'Sample subitle'
    assert course_obj.price == Decimal('99.99')
    assert course_obj.is_free == False

    # Success - description and free tag changed
    serializer = CourseSerializer(
        course1,
        data={
            'description': 'New description',
            'is_free': 'true'
        },
        partial=True
    )
    course_obj = serializer.save(user=user1)
    assert course_obj.description == 'New description'
    assert course_obj.price == Decimal('0.00')
    assert Course.objects.fetch_courses().count() == 0

    # Partial success - published course but cannot change slug
    serializer = CourseSerializer(
        course1,
        data={
            'slug': 'new-course-slug',
            'is_draft': 'false'
        },
        partial=True
    )
    course_obj = serializer.save(user=user1)
    assert course_obj.slug == course1.slug
    assert Course.objects.fetch_courses().count() == 1


def test_unauthorized_course_serializer_update(test_user, sample_course):
    '''Testing CourseSerializer throws error unless instructor updates course'''

    # Non-admin user
    user1 = test_user()

    # Test course
    course1 = sample_course()

    # Non-admin non-instructor trying to update course
    serializer = CourseSerializer(
        course1,
        data={'title': 'Changed title'},
        partial=True
    )
    with pytest.raises(Exception) as e:
        serializer.save(user=user1)
    assert str(e.value) == 'Only an instructor of a course can update a course'


def test_duplicate_title_serializer_update(test_user, sample_course):
    '''Testing CourseSerializer throws error if title is duplicate'''

    # Non-admin user
    user1 = test_user()
    user1.is_staff = True
    user1.save()

    # Test course
    course1 = sample_course()

    course1.add_instructor(user1)

    # Second sample course
    course2 = sample_course(index=2)

    # Cannot make first course title same as second course
    serializer = CourseSerializer(
        course1,
        data={'title': course2.title.lower()},
        partial=True
    )
    with pytest.raises(Exception) as e:
        course_obj = serializer.save(user=user1)
    assert str(e.value) == 'A course with this title already exists'
