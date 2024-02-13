import pytest

from courses.tests.fixtures import sample_course
from fixtures import test_lectures
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


def test_change_lecture_order(sample_course, test_lectures):
    '''Test manager method for changing order of lectures in a course'''

    # Test course
    course1 = sample_course

    # Test lectures
    lectures = test_lectures(course1, 3)

    # Fail - can't move first lecture up
    with pytest.raises(Exception) as e:
        Lecture.objects.change_lecture_order(lectures[0])
    assert (str(e.value)) == 'Lecture is already the first in the course'

    Lecture.objects.change_lecture_order(lectures[1])
    check_lectures = Lecture.objects.all()
    assert check_lectures[0].title == lectures[1].title
    assert check_lectures[1].title == lectures[0].title
    assert check_lectures[2].title == lectures[2].title

    Lecture.objects.change_lecture_order(lectures[2], 'Up')
    check_lectures = Lecture.objects.all()
    assert check_lectures[0].title == lectures[1].title
    assert check_lectures[1].title == lectures[2].title
    assert check_lectures[2].title == lectures[0].title

    Lecture.objects.change_lecture_order(lectures[2], 'DowN')
    check_lectures = Lecture.objects.all()
    assert check_lectures[0].title == lectures[1].title
    assert check_lectures[1].title == lectures[0].title
    assert check_lectures[2].title == lectures[2].title

    # Fail - can't move last lecture down
    with pytest.raises(Exception) as e:
        Lecture.objects.change_lecture_order(lectures[2], 'DowN')
    assert (str(e.value)) == 'Lecture is already the last in the course'

    # Fail - only two directions allowed
    with pytest.raises(Exception) as e:
        Lecture.objects.change_lecture_order(lectures[2], 'DowNN')
    assert (str(
        e.value)) == 'Direction in which the lecture needs to be moved can be up or down'
