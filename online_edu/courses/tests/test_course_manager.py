import pytest

from courses.models import Course
from .fixtures import sample_courses

pytestmark = pytest.mark.django_db


def test_course_manager(sample_courses):
    '''Test CourseManager'''

    # Create five random courses
    test_courses = sample_courses(5)

    # All course are draft
    courses_found = Course.objects.fetch_courses()
    assert courses_found.count() == 0

    # Looking for draft courses
    courses_found = Course.objects.fetch_courses(is_draft=True)
    assert courses_found.count() == 5

    # Publishing course 2
    test_courses[2].is_draft = False
    test_courses[2].save()

    # One course fetched
    courses_found = Course.objects.fetch_courses()
    assert courses_found.count() == 1
    assert courses_found[0].title == test_courses[2].title

    # Publishing course 4
    test_courses[4].is_draft = False
    test_courses[4].save()

    # Two courses fetched
    courses_found = Course.objects.fetch_courses()
    assert courses_found.count() == 2
    assert courses_found[0].title == test_courses[2].title
    assert courses_found[1].title == test_courses[4].title

    # Archiving course 4
    test_courses[4].is_archived = True
    test_courses[4].save()

    # One course fetched
    courses_found = Course.objects.fetch_courses()
    assert courses_found.count() == 1

    # No courses that are draft and archived
    courses_found = Course.objects.fetch_courses(
        is_draft=True, is_archived=True)
    assert courses_found.count() == 0

    # One archived course found
    courses_found = Course.objects.fetch_courses(is_archived=True)
    assert courses_found.count() == 1
    assert courses_found[0].title == test_courses[4].title
