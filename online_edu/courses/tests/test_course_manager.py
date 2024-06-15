import pytest

from courses.models import Course
from .fixtures import sample_course, sample_courses

pytestmark = pytest.mark.django_db


def test_course_fetch_query(sample_courses):
    '''Test custom query of CourseManager'''

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


def test_course_query_by_slug(sample_course):
    '''Test query by slug in CourseManager'''

    course = sample_course()

    # By default, query is run with admin privileges
    course_found = Course.objects.get_course_by_slug(course.slug)
    assert course_found.title == course.title

    # With regular user auth, 404 is returned for draft courses
    with pytest.raises(Exception):
        course_found = Course.objects.get_course_by_slug(
            course.slug,
            admin_only=False
        )

    # Published course
    course.is_draft = False
    course.save()

    # Published course can be found by regular user auth
    course_found = Course.objects.get_course_by_slug(
        course.slug,
        admin_only=False
    )
    assert course_found.title == course.title

    # Archive the course
    course.is_archived = True
    course.save()

    # Archived courses cannot be found by regular user
    with pytest.raises(Exception):
        course_found = Course.objects.get_course_by_slug(
            course.slug,
            admin_only=False
        )

    # Archived courses can be found by admin user
    course_found = Course.objects.get_course_by_slug(course.slug)
    assert course_found.title == course.title


def test_check_if_title_duplicate(sample_course):
    '''
    Test for query that checks if title is duplicate
    '''

    course1 = sample_course()

    # Title case not the same, but course excluded
    result = Course.objects.check_if_title_duplicate(
        course1.id, course1.title.lower())
    assert result == False

    with pytest.raises(Exception) as e:
        Course.objects.check_if_title_duplicate(None, course1.title.lower())
