import pytest
import json
from rest_framework.test import APIClient

from courses.models import Course
from .fixtures import sample_course, sample_courses

pytestmark = pytest.mark.django_db


def test_course_fetch_all(sample_courses):
    '''Test get all courses endpoint'''

    client = APIClient()

    # Create sample courses - all in draft mode
    courses = sample_courses(5)

    # No course returned - all in draft
    api_response = client.get('/api/courses/', format='json')
    assert api_response.status_code == 200
    assert len(api_response.data) == 0

    # Make second course not draft
    courses[1].is_draft = False
    courses[1].save()

    # One course returned
    api_response = client.get('/api/courses/', format='json')
    assert api_response.status_code == 200
    assert len(api_response.data) == 1
    api_response.render()
    api_response = json.loads(api_response.content)
    assert api_response[0]['title'] == courses[1].title

    # Make fourth course not draft
    courses[3].is_draft = False
    courses[3].save()

    # Two courses returned
    api_response = client.get('/api/courses/', format='json')
    assert api_response.status_code == 200
    assert len(api_response.data) == 2
    api_response.render()
    api_response = json.loads(api_response.content)
    assert api_response[0]['title'] == courses[1].title
    assert api_response[1]['title'] == courses[3].title

    # Make last course not draft
    courses[4].is_draft = False
    courses[4].save()

    # Three courses returned
    api_response = client.get('/api/courses/', format='json')
    assert api_response.status_code == 200
    assert len(api_response.data) == 3
    api_response.render()
    api_response = json.loads(api_response.content)
    assert api_response[0]['title'] == courses[1].title
    assert api_response[1]['title'] == courses[3].title
    assert api_response[2]['title'] == courses[4].title

    # Make fourth course as archived
    courses[3].is_archived = True
    courses[3].save()

    # Two courses should be returned
    api_response = client.get('/api/courses/', format='json')
    assert api_response.status_code == 200
    assert len(api_response.data) == 2
    api_response.render()
    api_response = json.loads(api_response.content)
    assert api_response[0]['title'] == courses[1].title
    assert api_response[1]['title'] == courses[4].title


def test_course_fetch_detail(sample_course):
    '''Test retrieve course endpoint'''

    client = APIClient()

    # Sample draft course
    course = sample_course

    # Should give 404 as course is in draft mode
    api_response = client.get(
        '/api/courses/{}'.format(course.slug),
        format='json'
    )
    assert api_response.status_code == 404

    # Set draft to false
    course.is_draft = False
    course.save()
    # Should be retrieved
    api_response = client.get(
        '/api/courses/{}'.format(course.slug),
        format='json'
    )
    assert api_response.status_code == 200
    assert api_response.data['title'] == course.title

    # Use wrong slug
    api_response = client.get(
        '/api/courses/{}'.format(course.slug + '1'),
        format='json'
    )
    assert api_response.status_code == 404

    # Make course archived
    course.is_archived = True
    course.save()
    # Should give 404
    api_response = client.get(
        '/api/courses/{}'.format(course.slug),
        format='json'
    )
    assert api_response.status_code == 404
