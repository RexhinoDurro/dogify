# middleware.py - Simplified for API-only bot detection
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
    # Check various headers for the real IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = (request.META.get('HTTP_X_REAL_IP') or 
              request.META.get('HTTP_CF_CONNECTING_IP') or
              request.META.get('REMOTE_ADDR'))
    
    return ip

class BotProtectionMiddleware:
    """Lightweight middleware for API protection only"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit_requests = getattr(settings, 'RATE_LIMIT_REQUESTS_PER_MINUTE', 100)
        
        # Critical bot patterns that should be blocked immediately
        self.critical_bot_patterns = [
            re.compile(r'facebook|facebookexternalhit|facebot', re.I),
            re.compile(r'curl|wget|python-requests', re.I),
            re.compile(r'scrapy|selenium|headless', re.I),
        ]
        
        # Honeypot paths
        self.honeypot_paths = [
            '/wp-admin/', '/wp-login.php', '/admin/', '/administrator/',
            '/phpmyadmin/', '/.env', '/config.php', '/backup/',
            '/.git/', '/.svn/', '/xmlrpc.php'
        ]
    
    def __call__(self, request):
        # Start timing
        request._start_time = time.time()
        
        # Get client IP
        client_ip = get_client_ip(request)
        request.client_ip = client_ip
        
        # Skip protection for API endpoints (they handle their own detection)
        if self._should_skip_protection(request):
            return self.get_response(request)
        
        # 1. IP Blacklist Check (only for critical cases)
        if self._is_ip_blacklisted(client_ip):
            return self._create_blocked_response('IP blacklisted', client_ip)
        
        # 2. Rate Limiting Check
        if self._check_rate_limit(client_ip):
            return self._create_rate_limit_response()
        
        # 3. Honeypot Check
        if self._is_honeypot_access(request):
            self._handle_honeypot_trigger(client_ip, request)
            return self._create_blocked_response('Unauthorized access', client_ip)
        
        # 4. Critical Bot Detection (only block the most obvious bots)
        if self._critical_bot_detection(request):
            self._add_to_blacklist(client_ip, 'Critical bot pattern detected', 0.95, request)
            return self._create_blocked_response('Bot detected', client_ip)
        
        # 5. Log request pattern for analysis
        self._log_request_pattern(client_ip, request)
        
        # Process request
        response = self.get_response(request)
        self._add_security_headers(response)
        
        return response
    
    def _should_skip_protection(self, request):
        """Skip protection for API and admin endpoints"""
        # Skip for API endpoints - they handle their own detection
        if request.path.startswith('/api/'):
            return True
        
        # Skip for admin panel
        if request.path.startswith('/admin/'):
            return True
        
        # Skip for health checks
        if request.path in ['/health/', '/ping/', '/status/']:
            return True
        
        return False
        
    def _is_ip_blacklisted(self, ip_address):
        """Check if IP is blacklisted (with caching)"""
        return IPBlacklist.is_blacklisted(ip_address)
    
    def _check_rate_limit(self, ip_address):
        """Check if IP is exceeding rate limits"""
        cache_key = f"rate_limit_{ip_address}"
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= self.rate_limit_requests:
            # Log rate limit exceeded
            SecurityLog.log_event(
                event_type='rate_limit_exceeded',
                ip_address=ip_address,
                description=f'Rate limit exceeded: {current_requests} requests/minute',
                severity='medium',
                details={
                    'requests_count': current_requests,
                    'limit': self.rate_limit_requests
                }
            )
            return True
        
        # Increment counter
        cache.set(cache_key, current_requests + 1, 60)  # 1 minute window
        return False
    
    def _is_honeypot_access(self, request):
        """Check if request is accessing honeypot paths"""
        path = request.path.lower()
        return any(honeypot in path for honeypot in self.honeypot_paths)
    
    def _critical_bot_detection(self, request):
        """Critical bot detection - only block obvious bots"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        if not user_agent:
            return True  # No user agent is highly suspicious
        
        # Check against critical bot patterns only
        for pattern in self.critical_bot_patterns:
            if pattern.search(user_agent):
                return True
        
        return False
    
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
                response_code=200,  # Will be updated if needed
                response_time=0,    # Will be calculated later
                user_agent_hash=user_agent_hash
            )
        except Exception as e:
            print(f"Failed to log request pattern: {e}")
    
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
                    'user_agent': user_agent[:500],  # Limit length
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
            
            # Clear cache
            cache.delete(f"blacklist_{ip_address}")
            
            # Log security event
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
        """Create standardized blocked response"""
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
        """Add security headers to response"""
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['X-Security-Check'] = 'passed'

class RequestTimingMiddleware:
    """Middleware to track request timing"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Add timing header
        response['X-Response-Time'] = f"{response_time:.3f}s"
        
        # Update request pattern if exists
        if hasattr(request, 'client_ip'):
            self._update_request_timing(request, response_time, response.status_code)
        
        return response
    
    def _update_request_timing(self, request, response_time, status_code):
        """Update request timing in database"""
        try:
            # Find recent request pattern to update
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
            print(f"Failed to update request timing: {e}")