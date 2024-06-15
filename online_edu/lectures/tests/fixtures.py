import pytest

from courses.tests.fixtures import sample_course
from lectures.models import Lecture

pytestmark = pytest.mark.django_db

TEST_LECTURE_TITLE = 'Lecture'
TEST_LECTURE_DESCRIPTION = 'Lecture description'


@pytest.fixture
def test_lecture(sample_course):
    '''
    Generate a test lecture

    Parametrs
    ----------------
    course: Course model instance (optional)
    title: str (optional)
        Title of the lecture. Default value is "Lecture <index>"
    description: str (optional)
        Description of the lecture. Default value is "Lecture description <index>"
    index: int (optional)
        Index of the lecture. Default value is 1.

    Returns
    ----------------
    Lecture model instance
    '''
    def _gen_lecture(course=None, title=None, description=None, index=1):
        if course is None:
            course = sample_course()
        if title is None:
            title = f'{TEST_LECTURE_TITLE} {index}'
        if description is None:
            description = f'{TEST_LECTURE_DESCRIPTION} {index}'
        return Lecture.objects.create(
            course=course,
            title=title,
            description=description
        )

    return _gen_lecture


@pytest.fixture
def test_lectures(test_lecture, sample_course):
    '''
    Generates an array of test lectures (test_lecture above)

    Parameters
    --------------
    course: Course model instance
    no_of_lectures: int (optional)
        Number of test lectures to be created. Default is 1.
    '''
    def _gen_lectures(course=None, no_of_lectures=None):
        if course is None:
            course = sample_course()
        if no_of_lectures is None:
            no_of_lectures = 1
        lectures = [test_lecture(course=course, index=i+1)
                    for i in range(no_of_lectures)]
        return lectures

    return _gen_lectures
