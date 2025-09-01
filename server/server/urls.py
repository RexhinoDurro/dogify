# server/server/urls.py - Updated URL configuration
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('bot_detection.urls')),
]