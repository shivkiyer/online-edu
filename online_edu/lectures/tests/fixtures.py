import pytest

from courses.tests.fixtures import sample_course
from lectures.models import Lecture

pytestmark = pytest.mark.django_db


@pytest.fixture
def test_lectures(sample_course):
    def _gen_lectures(course, no_of_lectures):
        if course is None:
            course = sample_course
        if no_of_lectures is None:
            no_of_lectures = 1
        lectures = [Lecture.objects.create(
            course=course,
            title='Lec {}'.format(str(i)),
            description='Lec {} descr'.format(str(i))
        ) for i in range(no_of_lectures)]
        return lectures

    return _gen_lectures
