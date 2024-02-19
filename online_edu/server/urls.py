from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('user_auth.urls', namespace='user_auth')),
    path('api/courses/', include('courses.urls', namespace='courses')),
    path('api/registration/', include('registration.urls', namespace='registration')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
