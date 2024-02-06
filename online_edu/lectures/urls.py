from django.urls import path

from .views import LectureView

app_name = 'lectures'
urlpatterns = [
    path(
        'new-lecture',
        LectureView.as_view(),
        name='create-lecture'
    ),
    path(
        '',
        LectureView.as_view(),
        name='fetch-lectures'
    ),
    path(
        '<int:id>',
        LectureView.as_view(),
        name='fetch-edit-lecture'
    ),
]
