from django.urls import path, include

from .views import CourseView

app_name = 'courses'
urlpatterns = [
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
        '<str:slug>/lectures/',
        include('lectures.urls', namespace='lectures')
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
