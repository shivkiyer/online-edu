import pytest

from courses.tests.fixtures import sample_course
from courses.models import Course
from user_auth.tests.fixtures import test_user
from lectures.serializers import LectureSerializer
from lectures.models import Lecture
from lectures.tests.fixtures import test_lecture, test_lectures

pytestmark = pytest.mark.django_db


def test_lecture_serializer_create(sample_course, test_user):
    '''Testing creating model instance from serializer'''

    # Test user
    user1 = test_user()
    user1.is_staff = True
    user1.save()

    # Test course
    course1 = sample_course()

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

    # Create another test course
    course2 = sample_course(index=2)
    course2.add_instructor(user1)

    # Success - same title, different courses
    serializer = LectureSerializer(data={'title': 'Lec 1'})
    serializer.save(user=user1, course=course2)
    assert Lecture.objects.all().count() == 3


def test_unauthorized_serializer(sample_course, test_user):
    '''Testing to verify that only instructor can create lecture'''

    # Test user
    user1 = test_user()

    # Test course
    course1 = sample_course()

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


def test_lecture_serializer_bad_data(sample_course, test_user):
    '''Testing lecture serializer handling bad data'''

    # Test user
    user1 = test_user()
    user1.is_staff = True
    user1.save()

    # Test course
    course1 = sample_course()

    course1.add_instructor(user1)

    # Fail - title is required
    serializer = LectureSerializer(data={})
    with pytest.raises(Exception) as e:
        serializer.save(user=user1, course=course1)
    assert str(e.value) == 'The title of a lecture is required'


def test_lecture_duplicate_title(sample_course, test_user, test_lecture):
    '''Testing serializer prevents duplicate title within same course'''

    # Test user
    user1 = test_user()
    user1.is_staff = True
    user1.save()

    # Test course
    course1 = sample_course()

    course1.add_instructor(user1)

    lecture1 = test_lecture(course=course1)

    # Fail - duplicate lecture title in same course
    serializer = LectureSerializer(data={'title': lecture1.title.lower()})
    with pytest.raises(Exception) as e:
        serializer.save(user=user1, course=course1)
    assert str(e.value) == 'Lecture with the same title exists in the course'


def test_lecture_serializer_update(sample_course, test_user, test_lecture):
    '''Test for updating lecture instance with serializer'''

    # Test user
    user1 = test_user()
    user1.is_staff = True
    user1.save()

    # Test course
    course1 = sample_course()

    # Make user instructor
    course1.add_instructor(user1)

    # Test lecture
    lecture1 = test_lecture(course=course1)

    # Success - change only title
    serializer = LectureSerializer(
        lecture1,
        {'title': 'New lecture 1'},
        partial=True
    )
    serializer.save(user=user1, course=course1)
    assert Lecture.objects.all()[0].title == 'New lecture 1'
    assert Lecture.objects.all()[0].description == lecture1.description

    # Success - change only description
    serializer = LectureSerializer(
        lecture1,
        {'description': 'New lec 1 description'},
        partial=True
    )
    serializer.save(user=user1, course=course1)
    assert Lecture.objects.all()[0].description == 'New lec 1 description'


def test_unauthorized_lecture_serializer_update(sample_course, test_user, test_lecture):
    '''Test that serializer throws error unless user is instructor'''

    # Test user
    user1 = test_user()

    # Test course
    course1 = sample_course()

    # Test lecture
    lecture1 = test_lecture(course=course1)

    # Fail - non-admin user trying to update lecture
    serializer = LectureSerializer(
        lecture1,
        {'title': 'New lecture 1'},
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
        {'title': 'New lecture 1'},
        partial=True
    )
    with pytest.raises(Exception) as e:
        serializer.save(user=user1, course=course1)
    assert str(
        e.value) == 'Must be an instructor of the course to create or update lectures'


def test_lecture_serializer_bad_data(sample_course, test_user, test_lecture):
    '''Test for serializer handling bad data'''

    # Test user
    user1 = test_user()
    user1.is_staff = True
    user1.save()

    # Test course
    course1 = sample_course()

    # Make user instructor
    course1.add_instructor(user1)

    # Test lecture
    lecture1 = test_lecture(course=course1)

    # Fail - empty serializer - nothing to update
    serializer = LectureSerializer(
        lecture1,
        {},
        partial=True
    )
    with pytest.raises(Exception) as e:
        serializer.save(user=user1, course=course1)
    assert str(e.value) == 'Empty request body'


def test_serializer_duplicate_lecture_title(sample_course, test_user, test_lectures):
    '''Test that serializer checks for duplicate lecture title in same course'''

    # Test user
    user1 = test_user()
    user1.is_staff = True
    user1.save()

    # Test course
    course1 = sample_course()

    # Make user instructor
    course1.add_instructor(user1)

    # Test lectures
    lecture1, lecture2 = test_lectures(course=course1, no_of_lectures=2)

    # Fail - duplicate title
    serializer = LectureSerializer(
        lecture2,
        {'title': 'Lecture 1'},
        partial=True
    )
    with pytest.raises(Exception) as e:
        serializer.save(user=user1, course=course1)
    assert str(e.value) == 'Lecture with the same title exists in the course'
