from django.urls import path

from .views import CourseCreateView

app_name = 'courses'
urlpatterns = [
    path(
        'new-course',
        CourseCreateView.as_view(),
        name='create-course'
    ),
]
