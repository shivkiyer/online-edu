from django.urls import path

from .views import LectureView, AdjustLectureOrderView

app_name = 'lectures'
urlpatterns = [
    path(
        'new-lecture',
        LectureView.as_view(),
        name='create-lecture'
    ),
    path(
        '<int:id>/move-lecture/<str:direction>',
        AdjustLectureOrderView.as_view(),
        name='move-lecture'
    ),
    path(
        '<int:id>',
        LectureView.as_view(),
        name='fetch-edit-lecture'
    ),
    path(
        '',
        LectureView.as_view(),
        name='fetch-lectures'
    ),
]
