from django.urls import path

from .views import CourseRegisterView, CourseInstructorAddView

app_name = 'registration'
urlpatterns = [
    path(
        '<str:slug>/register-student',
        CourseRegisterView.as_view(),
        name='register-course'
    ),
    path(
        '<str:slug>/add-instructor',
        CourseInstructorAddView.as_view(),
        name='add-instructor'
    ),
]
