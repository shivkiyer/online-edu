import pytest

from courses.tests.fixtures import sample_course
from courses.models import Course
from user_auth.tests.fixtures import test_user
from lectures.serializers import LectureSerializer
from lectures.models import Lecture

pytestmark = pytest.mark.django_db


def test_lecture_serializer_create(sample_course, test_user):
    '''Testing creating model instance from serializer'''

    # Test user
    user1 = test_user()

    # Test course
    course1 = sample_course

    # Fail - title is required
    serializer = LectureSerializer(data={})
    with pytest.raises(Exception) as e:
        serializer.save(user=user1, course=course1)
    assert str(e.value) == 'The title of a lecture is required'

    # Fail - non-admin user cannot create lecture
    serializer = LectureSerializer(data={'title': 'Lec 1'})
    with pytest.raises(Exception) as e:
        serializer.save(user=user1, course=course1)
    assert str(
        e.value) == 'Must be an instructor of the course to create or update lectures'

    # Make user admin
    user1.is_staff = True
    user1.save()

    # Fail - only instructors can create lecture
    serializer = LectureSerializer(data={'title': 'Lec 1'})
    with pytest.raises(Exception) as e:
        serializer.save(user=user1, course=course1)
    assert str(
        e.value) == 'Must be an instructor of the course to create or update lectures'

    # Make user instructor
    course1.add_instructor(user1)

    # Success
    serializer = LectureSerializer(data={'title': 'Lec 1'})
    serializer.save(user=user1, course=course1)
    assert Lecture.objects.all().count() == 1

    # Success
    serializer = LectureSerializer(data={'title': 'Lec 2'})
    serializer.save(user=user1, course=course1)
    assert Lecture.objects.all().count() == 2

    # Fail - duplicate lecture title in same course
    serializer = LectureSerializer(data={'title': 'Lec 1'})
    with pytest.raises(Exception) as e:
        serializer.save(user=user1, course=course1)
    assert str(e.value) == 'Lecture with the same title exists in the course'

    # Create another test course
    course2 = Course.objects.create(
        title='Some course',
        description='Some descr',
        is_free=True
    )
    course2.add_instructor(user1)

    # Success - same title, different courses
    serializer = LectureSerializer(data={'title': 'Lec 1'})
    serializer.save(user=user1, course=course2)
    assert Lecture.objects.all().count() == 3


def test_lecture_serializer_update(sample_course, test_user):
    '''Test for updating lecture instance with serializer'''

    # Test user
    user1 = test_user()

    # Test course
    course1 = sample_course

    # Test lecture
    lecture1 = Lecture.objects.create(
        course=course1,
        title='Lec 1',
        description='Lec 1 descr'
    )

    # Fail - empty serializer - nothing to update
    serializer = LectureSerializer(
        lecture1,
        {},
        partial=True
    )
    with pytest.raises(Exception) as e:
        serializer.save(user=user1, course=course1)
    assert str(e.value) == 'Empty request body'

    # Fail - non-admin user trying to update lecture
    serializer = LectureSerializer(
        lecture1,
        {'title': 'New lec 1'},
        partial=True
    )
    with pytest.raises(Exception) as e:
        serializer.save(user=user1, course=course1)
    assert str(
        e.value) == 'Must be an instructor of the course to create or update lectures'

    # Make user admin
    user1.is_staff = True
    user1.save()

    # Fail - user not instructor
    serializer = LectureSerializer(
        lecture1,
        {'title': 'New lec 1'},
        partial=True
    )
    with pytest.raises(Exception) as e:
        serializer.save(user=user1, course=course1)
    assert str(
        e.value) == 'Must be an instructor of the course to create or update lectures'

    # Make user instructor
    course1.add_instructor(user1)

    # Success - change only title
    serializer = LectureSerializer(
        lecture1,
        {'title': 'New lec 1'},
        partial=True
    )
    serializer.save(user=user1, course=course1)
    assert Lecture.objects.all()[0].title == 'New lec 1'
    assert Lecture.objects.all()[0].description == 'Lec 1 descr'

    # Success - change only description
    serializer = LectureSerializer(
        lecture1,
        {'description': 'New lec 1 description'},
        partial=True
    )
    serializer.save(user=user1, course=course1)
    assert Lecture.objects.all()[0].description == 'New lec 1 description'

    # Create another lecture
    lecture2 = Lecture.objects.create(
        course=course1,
        title='Lec 2',
        description='Lec 2 descr'
    )

    # Fail - duplicate title
    serializer = LectureSerializer(
        lecture2,
        {'title': 'New lec 1'},
        partial=True
    )
    with pytest.raises(Exception) as e:
        serializer.save(user=user1, course=course1)
    assert str(e.value) == 'Lecture with the same title exists in the course'

    # Success - description changed
    serializer = LectureSerializer(
        lecture2,
        {'description': 'New lec 1 description'},
        partial=True
    )
    serializer.save(user=user1, course=course1)
    assert Lecture.objects.all()[1].description == 'New lec 1 description'

    # Success -title changed
    serializer = LectureSerializer(
        lecture2,
        {'title': 'New lec 2'},
        partial=True
    )
    serializer.save(user=user1, course=course1)
    assert Lecture.objects.all()[1].title == 'New lec 2'
