# bot_detection/urls.py - Updated URL patterns
from django.urls import path
from . import views

urlpatterns = [
    # Bot detection API endpoints
    path('bot-detection/detect/', views.BotDetectionView.as_view(), name='bot-detect'),
    path('bot-detection/security/bot-detected/', views.SecurityBotDetectionView.as_view(), name='security-bot-detect'),
    path('bot-detection/get-ip/', views.GetClientIPView.as_view(), name='get-client-ip'),
    path('bot-detection/health/', views.health_check, name='health-check'),
    
    # Admin/Management endpoints
    path('admin/stats/', views.BotStatisticsView.as_view(), name='bot-stats'),
    path('admin/blacklist/', views.BlacklistManagementView.as_view(), name='blacklist-management'),
    path('admin/retrain/', views.RetrainModelView.as_view(), name='retrain-model'),
    
    # Webhook endpoint
    path('webhook/threat-intel/', views.webhook_threat_intel, name='threat-intel-webhook'),
]