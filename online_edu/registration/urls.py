from django.urls import path

from .views import CourseRegisterView

app_name = 'registration'
urlpatterns = [
    path(
        '<str:slug>/register-student',
        CourseRegisterView.as_view(),
        name='register-course'
    ),
]
