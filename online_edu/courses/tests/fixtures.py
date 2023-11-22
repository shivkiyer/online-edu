import pytest
from random import randint
from faker import Faker

from courses.models import Course

fake = Faker()


@pytest.fixture
def sample_course():
    '''Generate a random free course'''
    return Course.objects.create(
        title=fake.name(),
        description=fake.text(),
        is_free=True
    )


@pytest.fixture
def sample_courses():
    '''Generate multiple random free course'''

    def _course_generator(no_of_courses):
        courses = [
            Course.objects.create(
                title=fake.name(),
                description=fake.text(),
                is_free=True
            ) for i in range(no_of_courses)
        ]

        return courses

    return _course_generator
