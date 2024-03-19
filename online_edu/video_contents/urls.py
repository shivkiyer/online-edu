from django.urls import path

from .views import VideoContentView

app_name = 'video_contents'

urlpatterns = [
    path(
        'add-video/<str:filename>',
        VideoContentView.as_view(),
        name='add-video'
    ),
]
