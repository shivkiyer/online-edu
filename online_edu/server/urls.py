from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('user_auth.urls', namespace='user_auth')),
    path('api/courses/', include('courses.urls', namespace='courses')),
]
