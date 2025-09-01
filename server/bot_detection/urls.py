# urls.py - Django URL configuration for bot detection
from django.urls import path, include
from django.contrib import admin
from . import views

# Bot detection API URLs
bot_detection_patterns = [
    path('detect/', views.BotDetectionView.as_view(), name='bot-detect'),
    path('security/bot-detected/', views.SecurityBotDetectionView.as_view(), name='security-bot-detect'),
    path('get-ip/', views.GetClientIPView.as_view(), name='get-client-ip'),
    path('health/', views.health_check, name='health-check'),
    path('webhook/threat-intel/', views.webhook_threat_intel, name='threat-intel-webhook'),
]

# Admin/Management URLs
admin_patterns = [
    path('stats/', views.BotStatisticsView.as_view(), name='bot-stats'),
    path('blacklist/', views.BlacklistManagementView.as_view(), name='blacklist-management'),
    path('retrain/', views.RetrainModelView.as_view(), name='retrain-model'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/bot-detection/', include(bot_detection_patterns)),
    path('api/admin/', include(admin_patterns)),
]
