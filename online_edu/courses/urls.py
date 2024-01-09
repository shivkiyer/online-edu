from django.urls import path

from .views import CourseView, CourseRegisterView

app_name = 'courses'
urlpatterns = [
    path(
        '<str:slug>/register-student',
        CourseRegisterView.as_view(),
        name='register-course'
    ),
    path(
        'new-course',
        CourseView.as_view(),
        name='create-course'
    ),
    path(
        '<str:slug>/publish',
        CourseView.as_view(),
        name='publish-course'
    ),
    path(
        '<str:slug>',
        CourseView.as_view(),
        name='fetch-course'
    ),
    path(
        '',
        CourseView.as_view(),
        name='fetch-courses'
    ),
]
