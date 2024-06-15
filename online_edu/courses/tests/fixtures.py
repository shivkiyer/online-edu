import pytest

from courses.models import Course

TEST_COURSE_TITLE = 'Course'
TEST_COURSE_DESCRIPTION = 'Course description'


@pytest.fixture
def sample_course():
    '''
    Generate a random free course

    Parameters
    -----------------
    title: str (optional)
        Title of the course. Default value is "Course <index>"
    description: str (optional)
        Description of the course. Default value is "Course description <index>"
    index: int (optional)
        The index of the course. Default value is 1.

    Returns
    -----------------
    Course model instance with:
    title = "Course <index>"
    description = "Course description <index>"
    is_free = True
    '''

    def _course_generator(title=None, description=None, index=1):
        if title is None:
            title = f'${TEST_COURSE_TITLE} ${index}'
        if description is None:
            description = f'${TEST_COURSE_DESCRIPTION} ${index}'
        return Course.objects.create(
            title=title,
            description=description,
            is_free=True
        )

    return _course_generator


@pytest.fixture
def sample_courses(sample_course):
    '''
    Generate multiple random free course

    Parameters
    ---------------
    no_of_courses: int
        Number of courses to be generated

    Returns
    ---------------
    Array of Course model instances (sample_course) with:
    index from 1 to no_of_courses+1
    '''

    def _course_generator(no_of_courses):
        courses = [
            sample_course(index=i+1) for i in range(no_of_courses)
        ]
        return courses

    return _course_generator
