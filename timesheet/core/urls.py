from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.base_app.urls')),
    path('user-base/', include('apps.user_app.urls')),
]
