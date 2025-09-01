# server/server/urls.py - Updated to handle all traffic
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import View
import requests
from bot_detection.middleware import get_client_ip
from bot_detection.bot_detection_service import BotDetectionService

# Initialize bot detection service
bot_service = BotDetectionService()

class TrafficRouterView(View):
    """Route all traffic based on bot detection"""
    
    def get(self, request):
        client_ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Quick bot detection based on user agent
        is_bot = self._quick_bot_check(user_agent)
        
        print(f"Traffic router: {client_ip} | UA: {user_agent[:60]} | Bot: {is_bot}")
        
        if is_bot:
            # Serve security/redirect page for bots
            return self._serve_security_page(request)
        else:
            # Redirect humans to main site
            return HttpResponseRedirect("http://localhost:5173")
    
    def _quick_bot_check(self, user_agent):
        """Quick server-side bot detection"""
        if not user_agent:
            return True
            
        bot_patterns = [
            'facebook', 'facebookexternalhit', 'facebot',
            'googlebot', 'bingbot', 'bot', 'crawler', 
            'spider', 'curl', 'wget', 'python', 'scraper'
        ]
        
        user_agent_lower = user_agent.lower()
        return any(pattern in user_agent_lower for pattern in bot_patterns)
    
    def _serve_security_page(self, request):
        """Serve the security page content for bots"""
        # Simple security page HTML
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Check</title>
            <meta name="robots" content="noindex, nofollow">
        </head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>🛡️ Security Check</h1>
            <p>Bot detected. Access restricted.</p>
            <p>If you're human, please visit our main site directly.</p>
            <script>
                // Optional: Still run JavaScript detection for advanced bots
                setTimeout(() => {
                    if (navigator.userAgent.includes('facebook')) {
                        window.location.href = 'https://facebook.com';
                    }
                }, 3000);
            </script>
        </body>
        </html>
        """
        return HttpResponse(html_content)

# URL patterns - IMPORTANT: This catches ALL traffic
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('bot_detection.urls')),
    
    # Catch-all pattern - routes all traffic through bot detection
    path('', TrafficRouterView.as_view(), name='traffic-router'),
    path('<path:path>', TrafficRouterView.as_view(), name='traffic-router-path'),
]