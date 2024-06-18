import pytest
import time
from rest_framework.test import APIClient

from user_auth.tests.fixtures import test_user, access_token
from .fixtures import sample_course
from courses.models import Course

pytestmark = pytest.mark.django_db


def test_course_creation_endpoint(test_user, access_token):
    '''
    Tests for creating new course
    '''

    client = APIClient()

    user1 = test_user()
    user1.is_staff = True
    user1.save()

    token = access_token(user1, 60)

    # Success - admin user creates a new course
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Some course title',
            'description': 'Some course description',
            'price': 3.99
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 201
    assert Course.objects.count() == 1

    # Success - another course with different title
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Another course title',
            'description': 'Some course description',
            'price': 3.99
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 201
    assert Course.objects.count() == 2

    # Success - a free course with new title
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Some other course title',
            'description': 'Some course description',
            'is_free': True
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 201
    assert Course.objects.count() == 3


def test_unauthorized_course_creation(test_user, access_token):
    '''
    Test for non-admin users being prevented from creating courses
    '''

    client = APIClient()

    user1 = test_user()

    # Fail - no JWT is provided in header
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Some course title',
            'description': 'Some course description',
            'price': 3.99
        },
        format='json'
    )
    assert api_response.status_code == 403
    assert api_response.data['detail'] == 'Invalid login or inactive account'
    assert Course.objects.count() == 0

    # Fail - token in header is for non-admin user
    user1.is_staff = False
    user1.save()
    token = access_token(user1, 60)
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Some course title',
            'description': 'Some course description',
            'price': 3.99
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.data['detail'] == 'Admin privileges required for this action'
    assert api_response.status_code == 403
    assert Course.objects.count() == 0

    # Fail - expired token
    token = access_token(user1, 1)
    # Sleep for 2sec
    time.sleep(2)
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Another course title',
            'description': 'Some course description',
            'price': 3.99
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.data['detail'] == 'Must be logged in for this action'
    assert api_response.status_code == 403


def test_bad_course_data_failure(test_user, access_token):
    '''
    Tests for course creation failure due to missing data
    '''

    client = APIClient()

    user1 = test_user()
    user1.is_staff = True
    user1.save()

    token = access_token(user1, 60)

    # Fail - title missing
    api_response = client.post(
        '/api/courses/new-course',
        {
            'description': 'Some course description',
            'price': 3.99
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.data['detail'] == 'Course title is required'
    assert api_response.status_code == 400
    assert Course.objects.count() == 0

    # Fail - description missing
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Another course title',
            'price': 3.99
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.data['detail'] == 'Course description is required'
    assert api_response.status_code == 400
    assert Course.objects.count() == 0

    # Fail - price missing
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Another course title',
            'description': 'Some course description',
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.data['detail'] == 'Course price is required'
    assert api_response.status_code == 400
    assert Course.objects.count() == 0

    # Fail - price is 0.00 but course is not free
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Another course title',
            'description': 'Some course description',
            'price': 0.00
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.data['detail'] == 'Course price is required'
    assert api_response.status_code == 400
    assert Course.objects.count() == 0


def test_duplicate_course_title_failure(test_user, access_token, sample_course):
    '''
    Tests for course creation failure due to duplicate title
    '''

    client = APIClient()

    user1 = test_user()
    user1.is_staff = True
    user1.save()

    # Create test course
    course1 = sample_course()

    token = access_token(user1, 60)

    # Fail - duplicate title
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': course1.title,
            'description': 'Some course description',
            'price': 3.99
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.data['detail'] == 'A course with this title already exists'
    assert api_response.status_code == 400
    assert Course.objects.count() == 1


def test_course_create_with_translation(test_user, access_token):
    '''Test the creation of the course in supported languages'''

    client = APIClient()

    user1 = test_user()
    user1.is_staff = True
    user1.save()

    token = access_token(user1, 60)

    # Basic German content with de header
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'German title',
            'subtitle': 'German subtitle',
            'description': 'German description',
            'is_free': 'True'
        },
        headers={
            'Authorization': f'Bearer {token}',
            'Accept-Language': 'de'
        },
        format='json'
    )
    assert api_response.status_code == 201

    course1 = Course.objects.all()[0]
    assert course1.title == 'German title'
    assert course1.title_en == 'German title'
    assert course1.title_de == 'German title'
    assert course1.subtitle == 'German subtitle'
    assert course1.subtitle_en == 'German subtitle'
    assert course1.subtitle_de == 'German subtitle'
    assert course1.description == 'German description'
    assert course1.description_en == 'German description'
    assert course1.description_de == 'German description'

    # No language should default to English content
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Title',
            'subtitle': 'Subtitle',
            'description': 'Description',
            'is_free': 'True'
        },
        headers={
            'Authorization': f'Bearer {token}'
        },
        format='json'
    )
    assert api_response.status_code == 201

    course2 = Course.objects.all()[1]
    assert course2.title == 'Title'
    assert course2.title_de == 'Title'
    assert course2.title_en == 'Title'
    assert course2.subtitle == 'Subtitle'
    assert course2.subtitle_de == 'Subtitle'
    assert course2.subtitle_en == 'Subtitle'
    assert course2.description == 'Description'
    assert course2.description_de == 'Description'
    assert course2.description_en == 'Description'

    # Unsupported language (Portugese) should create default language content
    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Default title',
            'subtitle': 'Default subtitle',
            'description': 'Default description',
            'is_free': 'True'
        },
        headers={
            'Authorization': f'Bearer {token}',
            'Accept-language': 'pt_BR'
        },
        format='json'
    )
    assert api_response.status_code == 201

    # Country specific variation of language should
    # create basic language content
    course3 = Course.objects.all()[2]
    assert course3.title == 'Default title'
    assert course3.title_de == 'Default title'
    assert course3.title_en == 'Default title'
    assert course3.subtitle == 'Default subtitle'
    assert course3.subtitle_de == 'Default subtitle'
    assert course3.subtitle_en == 'Default subtitle'
    assert course3.description == 'Default description'
    assert course3.description_de == 'Default description'
    assert course3.description_en == 'Default description'

    api_response = client.post(
        '/api/courses/new-course',
        {
            'title': 'Austrian title',
            'subtitle': 'Austrian subtitle',
            'description': 'Austrian description',
            'is_free': 'True'
        },
        headers={
            'Authorization': f'Bearer {token}',
            'Accept-Language': 'de_AT'
        },
        format='json'
    )
    assert api_response.status_code == 201

    course4 = Course.objects.all()[3]
    assert course4.title == 'Austrian title'
    assert course4.title_en == 'Austrian title'
    assert course4.title_de == 'Austrian title'
    assert course4.subtitle == 'Austrian subtitle'
    assert course4.subtitle_en == 'Austrian subtitle'
    assert course4.subtitle_de == 'Austrian subtitle'
    assert course4.description == 'Austrian description'
    assert course4.description_en == 'Austrian description'
    assert course4.description_de == 'Austrian description'
