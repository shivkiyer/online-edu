import pytest

from courses.tests.fixtures import sample_course
from lectures.models import Lecture

pytestmark = pytest.mark.django_db


def test_lecture_duplicate_title(sample_course):
    '''Test for method to check for duplicate lecture titles'''

    # Test course
    course1 = sample_course

    # Test lecture within course
    lecture1 = Lecture.objects.create(
        course=course1,
        title="Lec 1"
    )

    # Method should raise exception of duplicate title in course
    with pytest.raises(Exception) as e:
        Lecture.objects.check_title_duplicate(course1, 'Lec 1')
    assert str(e.value) == 'Lecture with the same title exists in the course'

    # Method should return False if the lecture is excluded
    # This is so that during updating lectures no exception is raised
    check_result = Lecture.objects.check_title_duplicate(
        course1,
        'Lec 1',
        exclude_lecture=lecture1
    )
    assert check_result == False

    # Non-duplicate title
    check_result = Lecture.objects.check_title_duplicate(
        course1,
        'Lec 2'
    )
    assert check_result == False
