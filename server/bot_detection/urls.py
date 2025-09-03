# bot_detection/urls.py - Fixed to match existing views
from django.urls import path
from . import views

urlpatterns = [
    # Main bot detection endpoints (these exist in your current views.py)
    path('bot-detection/detect/', views.BotDetectionView.as_view(), name='bot-detect'),
    path('bot-detection/security/bot-detected/', views.SecurityBotDetectionView.as_view(), name='security-bot-detect'),
    path('bot-detection/get-ip/', views.GetClientIPView.as_view(), name='get-client-ip'),
    path('bot-detection/health/', views.health_check, name='health-check'),
    
    # Admin/Management endpoints (these exist in your current views.py)
    path('admin/stats/', views.BotStatisticsView.as_view(), name='bot-stats'),
    path('admin/blacklist/', views.BlacklistManagementView.as_view(), name='blacklist-management'),
    path('admin/retrain/', views.RetrainModelView.as_view(), name='retrain-model'),
    
    # Webhook endpoint (exists in your current views.py)
    path('webhook/threat-intel/', views.webhook_threat_intel, name='threat-intel-webhook'),
]