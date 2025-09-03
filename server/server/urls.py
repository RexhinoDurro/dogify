# server/server/urls.py - Simplified without redirecting bots
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.generic import View
from bot_detection.middleware import get_client_ip

class HealthCheckView(View):
    """Simple health check for the server"""
    
    def get(self, request):
        return JsonResponse({
            'status': 'healthy',
            'service': 'dogify-bot-detection',
            'version': '2.0.0'
        })

# URL patterns - Only API endpoints now
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('bot_detection.urls')),
    path('health/', HealthCheckView.as_view(), name='health-check'),
]