import pytest

from registration.models import CourseStudentRegistration
from courses.models import Course
from user_auth.tests.fixtures import test_user
from courses.tests.fixtures import sample_course

pytestmark = pytest.mark.django_db


def test_registration_manager(test_user, sample_course):
    '''Testing CourseStudentRegistrationManager'''

    user1 = test_user()
    course1 = sample_course()

    # Success - student appears in course students field
    registration1 = CourseStudentRegistration.objects.register_student(
        user=user1,
        course=course1
    )
    assert course1.students.all().count() == 1

    # Cannot register for course again
    with pytest.raises(Exception) as e:
        CourseStudentRegistration.objects.register_student(
            user=user1,
            course=course1
        )
    assert str(e.value) == 'User is already registered'

    # Create another student
    user2 = test_user(
        'anotheruser@domain.com',
        'password',
        False
    )
    # Registration successful - student count updated
    registration2 = CourseStudentRegistration.objects.register_student(
        user=user2,
        course=course1
    )
    assert course1.students.all().count() == 2

    # Create second course, register first student
    # Courses should appear in student reverse relationship
    course2 = sample_course(index=2)
    registration3 = CourseStudentRegistration.objects.register_student(
        user=user1,
        course=course2
    )
    assert user1.course_set.all().count() == 2
