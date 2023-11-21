from django.urls import path

from .views import CourseView

app_name = 'courses'
urlpatterns = [
    path(
        'new-course',
        CourseView.as_view(),
        name='create-course'
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
