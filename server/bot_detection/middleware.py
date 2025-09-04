# Fixed middleware.py - Much less aggressive bot detection
import time
import json
from django.core.cache import cache
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
import re

from .models import IPBlacklist, SecurityLog, RequestPattern

def get_client_ip(request):
    """Get the real client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = (request.META.get('HTTP_X_REAL_IP') or 
              request.META.get('HTTP_CF_CONNECTING_IP') or
              request.META.get('REMOTE_ADDR'))
    
    return ip

class BotProtectionMiddleware:
    """Much more lenient middleware - only blocks obvious bots"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit_requests = getattr(settings, 'RATE_LIMIT_REQUESTS_PER_MINUTE', 200)  # Increased
        
        # Only the most obvious bot patterns - very restrictive list
        self.obvious_bot_patterns = [
            re.compile(r'curl|wget', re.I),  # Command line tools
            re.compile(r'scrapy|mechanize', re.I),  # Scraping frameworks
            re.compile(r'python-requests|python-urllib', re.I),  # Python requests
        ]
        
        # Honeypot paths - only for obvious attack attempts
        self.honeypot_paths = [
            '/wp-admin/', '/wp-login.php', '/.env', '/config.php',
            '/phpmyadmin/', '/.git/', '/xmlrpc.php', '/admin.php'
        ]
    
    def __call__(self, request):
        request._start_time = time.time()
        client_ip = get_client_ip(request)
        request.client_ip = client_ip
        
        # Skip protection for most paths - only protect sensitive endpoints
        if self._should_skip_protection(request):
            return self.get_response(request)
        
        # 1. IP Blacklist Check (only for previously confirmed bots)
        if self._is_ip_blacklisted(client_ip):
            return self._create_blocked_response('IP blacklisted', client_ip)
        
        # 2. Very lenient rate limiting
        if self._check_rate_limit(client_ip):
            return self._create_rate_limit_response()
        
        # 3. Honeypot Check (only for obvious attack paths)
        if self._is_honeypot_access(request):
            self._handle_honeypot_trigger(client_ip, request)
            return self._create_blocked_response('Unauthorized access', client_ip)
        
        # 4. ONLY block the most obvious bots (not browsers)
        if self._is_obvious_bot(request):
            self._add_to_blacklist(client_ip, 'Obvious bot pattern detected', 0.95, request)
            return self._create_blocked_response('Bot detected', client_ip)
        
        # 5. Log request pattern for analysis (non-blocking)
        self._log_request_pattern(client_ip, request)
        
        response = self.get_response(request)
        self._add_security_headers(response)
        
        return response
    
    def _should_skip_protection(self, request):
        """Skip protection for most requests - be very permissive"""
        path = request.path.lower()
        
        # Skip for static files
        if any(path.endswith(ext) for ext in ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.woff2', '.ttf']):
            return True
        
        # Skip for admin panel
        if path.startswith('/admin/'):
            return True
        
        # Skip for health checks
        if path in ['/health/', '/ping/', '/status/']:
            return True
            
        # Skip for Django internal paths
        if path.startswith('/static/') or path.startswith('/media/'):
            return True
        
        return False
        
    def _is_ip_blacklisted(self, ip_address):
        """Check if IP is blacklisted (with caching)"""
        return IPBlacklist.is_blacklisted(ip_address)
    
    def _check_rate_limit(self, ip_address):
        """Very lenient rate limiting - only catch extreme abuse"""
        cache_key = f"rate_limit_{ip_address}"
        current_requests = cache.get(cache_key, 0)
        
        # Much higher threshold - 200 requests per minute
        if current_requests >= self.rate_limit_requests:
            SecurityLog.log_event(
                event_type='rate_limit_exceeded',
                ip_address=ip_address,
                description=f'Extreme rate limit exceeded: {current_requests} requests/minute',
                severity='medium',
                details={
                    'requests_count': current_requests,
                    'limit': self.rate_limit_requests
                }
            )
            return True
        
        cache.set(cache_key, current_requests + 1, 60)
        return False
    
    def _is_honeypot_access(self, request):
        """Check if request is accessing obvious attack paths"""
        path = request.path.lower()
        return any(honeypot in path for honeypot in self.honeypot_paths)
    
    def _is_obvious_bot(self, request):
        """Only detect the most obvious bots - NOT browsers"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Don't block missing user agent - some browsers/apps don't send it
        if not user_agent:
            return False  # Changed from True to False
        
        # Only block obvious automated tools
        for pattern in self.obvious_bot_patterns:
            if pattern.search(user_agent):
                return True
        
        # Don't block anything that looks like a browser
        browser_indicators = [
            'mozilla', 'chrome', 'safari', 'firefox', 'edge', 'opera',
            'webkit', 'gecko', 'mobile', 'android', 'iphone', 'ipad'
        ]
        
        user_agent_lower = user_agent.lower()
        if any(indicator in user_agent_lower for indicator in browser_indicators):
            return False  # It's a browser, don't block
        
        return False  # When in doubt, don't block
    
    def _log_request_pattern(self, ip_address, request):
        """Log request pattern for analysis"""
        try:
            import hashlib
            user_agent_hash = hashlib.md5(
                request.META.get('HTTP_USER_AGENT', '').encode()
            ).hexdigest()
            
            RequestPattern.objects.create(
                ip_address=ip_address,
                endpoint=request.path,
                method=request.method,
                response_code=200,
                response_time=0,
                user_agent_hash=user_agent_hash
            )
        except Exception as e:
            # Don't fail requests due to logging issues
            pass
    
    def _handle_honeypot_trigger(self, ip_address, request):
        """Handle honeypot trigger"""
        self._add_to_blacklist(ip_address, 'Honeypot triggered', 0.95, request)
        
        SecurityLog.log_event(
            event_type='honeypot_triggered',
            ip_address=ip_address,
            description=f'Honeypot triggered: {request.path}',
            severity='critical',
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={
                'path': request.path,
                'method': request.method,
                'referrer': request.META.get('HTTP_REFERER', '')
            }
        )
    
    def _add_to_blacklist(self, ip_address, reason, confidence, request):
        """Add IP to blacklist"""
        try:
            user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
            
            blacklist_entry, created = IPBlacklist.objects.get_or_create(
                ip_address=ip_address,
                defaults={
                    'reason': reason,
                    'confidence_score': confidence,
                    'detection_method': 'middleware_auto',
                    'user_agent': user_agent[:500],
                    'country_code': '',
                }
            )
            
            if not created:
                blacklist_entry.detection_count += 1
                blacklist_entry.confidence_score = max(
                    blacklist_entry.confidence_score,
                    confidence
                )
                blacklist_entry.save()
            
            cache.delete(f"blacklist_{ip_address}")
            
            SecurityLog.log_event(
                event_type='ip_blocked',
                ip_address=ip_address,
                description=f'IP automatically blacklisted: {reason}',
                severity='high',
                user_agent=user_agent,
                details={'confidence': confidence, 'reason': reason}
            )
            
        except Exception as e:
            print(f"Failed to add IP to blacklist: {e}")
    
    def _create_blocked_response(self, reason, ip_address):
        """Create blocked response"""
        from django.http import JsonResponse
        
        SecurityLog.log_event(
            event_type='access_blocked',
            ip_address=ip_address,
            description=f'Access blocked: {reason}',
            severity='high',
            details={'reason': reason}
        )
        
        return JsonResponse({
            'error': 'Access denied',
            'reason': 'Security policy violation',
            'code': 'BLOCKED',
            'timestamp': timezone.now().isoformat()
        }, status=403)
    
    def _create_rate_limit_response(self):
        """Create rate limit response"""
        from django.http import JsonResponse
        
        return JsonResponse({
            'error': 'Too many requests',
            'code': 'RATE_LIMITED',
            'retry_after': 60,
            'timestamp': timezone.now().isoformat()
        }, status=429)
    
    def _add_security_headers(self, response):
        """Add security headers"""
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

class RequestTimingMiddleware:
    """Middleware to track request timing"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        
        response_time = time.time() - start_time
        response['X-Response-Time'] = f"{response_time:.3f}s"
        
        if hasattr(request, 'client_ip'):
            self._update_request_timing(request, response_time, response.status_code)
        
        return response
    
    def _update_request_timing(self, request, response_time, status_code):
        """Update request timing in database"""
        try:
            recent_pattern = RequestPattern.objects.filter(
                ip_address=request.client_ip,
                endpoint=request.path,
                timestamp__gte=timezone.now() - timedelta(seconds=5)
            ).first()
            
            if recent_pattern:
                recent_pattern.response_time = response_time
                recent_pattern.response_code = status_code
                recent_pattern.save()
                
        except Exception as e:
            pass  # Don't fail requests due to timing update issues