# middleware.py - Django security middleware for bot protection
import time
import json
import hashlib
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from datetime import timedelta
import geoip2.database
import geoip2.errors
import re
import os

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
    """Main bot protection middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.blocked_countries = getattr(settings, 'BLOCKED_COUNTRIES', [])
        self.rate_limit_requests = getattr(settings, 'RATE_LIMIT_REQUESTS_PER_MINUTE', 100)
        self.enable_geo_blocking = getattr(settings, 'ENABLE_GEO_BLOCKING', True)
        
        # Load GeoIP database
        self.geoip_reader = None
        try:
            geoip_path = getattr(settings, 'GEOIP_PATH', None)
            if geoip_path and os.path.exists(os.path.join(geoip_path, 'GeoLite2-City.mmdb')):
                self.geoip_reader = geoip2.database.Reader(
                    os.path.join(geoip_path, 'GeoLite2-City.mmdb')
                )
        except Exception as e:
            print(f"GeoIP database not available: {e}")
        
        # Bot patterns for quick detection
        self.bot_patterns = [
            re.compile(r'facebook|facebookexternalhit|facebot', re.I),
            re.compile(r'bot|crawler|spider|scraper', re.I),
            re.compile(r'curl|wget|python|java', re.I),
            re.compile(r'headless|phantom|selenium', re.I),
        ]
        
        # Honeypot paths that should never be accessed by real users
        self.honeypot_paths = [
            '/wp-admin/', '/wp-login.php', '/admin/', '/administrator/',
            '/phpmyadmin/', '/.env', '/config.php', '/backup/',
            '/.git/', '/.svn/', '/xmlrpc.php', '/readme.html'
        ]
    
    def __call__(self, request):
        # Start timing for response time calculation
        request._start_time = time.time()
        
        # Get client IP
        client_ip = get_client_ip(request)
        request.client_ip = client_ip
        
        # Skip protection for internal/admin requests
        if self._should_skip_protection(request):
            return self.get_response(request)
        
        # 1. IP Blacklist Check (fastest check first)
        if self._is_ip_blacklisted(client_ip):
            return self._create_blocked_response(
                'IP blacklisted for bot activity',
                client_ip,
                request
            )
        
        # 2. Rate Limiting Check
        if self._check_rate_limit(client_ip, request):
            return self._create_rate_limit_response(client_ip, request)
        
        # 3. Geographic Blocking
        if self.enable_geo_blocking and self._is_geo_blocked(client_ip):
            return self._create_blocked_response(
                'Geographic restriction',
                client_ip,
                request
            )
        
        # 4. Honeypot Check
        if self._is_honeypot_access(request):
            self._handle_honeypot_trigger(client_ip, request)
            return self._create_blocked_response(
                'Unauthorized access attempt',
                client_ip,
                request
            )
        
        # 5. Quick Bot Detection (User Agent)
        if self._quick_bot_detection(request):
            self._add_to_blacklist(
                client_ip,
                'Bot user agent detected',
                0.9,
                request
            )
            return self._create_blocked_response(
                'Bot detected',
                client_ip,
                request
            )
        
        # 6. Suspicious Header Analysis
        if self._analyze_suspicious_headers(request):
            self._increment_suspicion(client_ip)
        
        # 7. Log request pattern
        self._log_request_pattern(client_ip, request)
        
        # Add security headers to response
        response = self.get_response(request)
        self._add_security_headers(response)
        
        return response
    
    def _should_skip_protection(self, request):
    
    # Skip for admin panel
        if request.path.startswith('/admin/'):
            return True
        
        # Skip for API endpoints - THIS IS IMPORTANT
        if request.path.startswith('/api/'):
            return True
        
        # Skip for API documentation
        if request.path.startswith('/docs/') or request.path.startswith('/swagger/'):
            return True
        
        # Skip for health checks
        if request.path in ['/health/', '/ping/', '/status/']:
            return True
        
        return False
        
    def _is_ip_blacklisted(self, ip_address):
        """Check if IP is blacklisted (with caching)"""
        return IPBlacklist.is_blacklisted(ip_address)
    
    def _check_rate_limit(self, ip_address, request):
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
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={
                    'requests_count': current_requests,
                    'path': request.path,
                    'method': request.method
                }
            )
            
            # Increment suspicion level
            self._increment_suspicion(ip_address)
            return True
        
        # Increment counter
        cache.set(cache_key, current_requests + 1, 60)  # 1 minute window
        return False
    
    def _is_geo_blocked(self, ip_address):
        """Check if IP is from a blocked country"""
        if not self.geoip_reader or not self.blocked_countries:
            return False
        
        try:
            response = self.geoip_reader.city(ip_address)
            country_code = response.country.iso_code
            return country_code in self.blocked_countries
        except geoip2.errors.AddressNotFoundError:
            return False
        except Exception:
            return False
    
    def _is_honeypot_access(self, request):
        """Check if request is accessing honeypot paths"""
        path = request.path.lower()
        return any(honeypot in path for honeypot in self.honeypot_paths)
    
    def _quick_bot_detection(self, request):
        """Quick bot detection based on user agent"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        if not user_agent:
            return True  # No user agent is highly suspicious
        
        # Check against bot patterns
        for pattern in self.bot_patterns:
            if pattern.search(user_agent):
                return True
        
        # Facebook bot specific check (highest priority)
        if re.search(r'facebook|facebookexternalhit|facebot', user_agent, re.I):
            return True
        
        return False
    
    def _analyze_suspicious_headers(self, request):
        """Analyze request headers for suspicious patterns"""
        headers = request.META
        suspicious_score = 0
        
        # Check for missing common headers
        if not headers.get('HTTP_ACCEPT'):
            suspicious_score += 0.3
        
        if not headers.get('HTTP_ACCEPT_LANGUAGE'):
            suspicious_score += 0.2
        
        if not headers.get('HTTP_ACCEPT_ENCODING'):
            suspicious_score += 0.15
        
        # Check for automation headers
        automation_headers = [
            'HTTP_X_REQUESTED_WITH',
            'HTTP_X_FORWARDED_FOR',
            'HTTP_X_REAL_IP'
        ]
        
        for header in automation_headers:
            if headers.get(header):
                suspicious_score += 0.1
        
        return suspicious_score >= 0.4
    
    def _log_request_pattern(self, ip_address, request):
        """Log request pattern for analysis"""
        try:
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
        self._add_to_blacklist(
            ip_address,
            'Honeypot triggered',
            0.95,
            request
        )
        
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
    
    def _increment_suspicion(self, ip_address):
        """Increment suspicion level for IP"""
        cache_key = f"suspicion_{ip_address}"
        current_level = cache.get(cache_key, 0)
        new_level = current_level + 1
        
        cache.set(cache_key, new_level, 3600)  # 1 hour expiry
        
        # Auto-blacklist if suspicion level is too high
        if new_level >= 5:
            self._add_to_blacklist(
                ip_address,
                f'High suspicion level: {new_level}',
                0.8,
                None
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
                    'user_agent': user_agent,
                    'country_code': self._get_country_code(ip_address),
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
    
    def _get_country_code(self, ip_address):
        """Get country code for IP address"""
        if not self.geoip_reader:
            return ''
        
        try:
            response = self.geoip_reader.city(ip_address)
            return response.country.iso_code or ''
        except:
            return ''
    
    def _create_blocked_response(self, reason, ip_address, request):
        """Create standardized blocked response"""
        SecurityLog.log_event(
            event_type='access_blocked',
            ip_address=ip_address,
            description=f'Access blocked: {reason}',
            severity='high',
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={
                'reason': reason,
                'path': request.path,
                'method': request.method
            }
        )
        
        return HttpResponseForbidden(
            json.dumps({
                'error': 'Access denied',
                'reason': 'Security policy violation',
                'code': 'BLOCKED',
                'timestamp': timezone.now().isoformat()
            }),
            content_type='application/json'
        )
    
    def _create_rate_limit_response(self, ip_address, request):
        """Create rate limit response"""
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
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['X-Security-Check'] = 'passed'
        
        # Add CSP header
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self';"
        )
        response['Content-Security-Policy'] = csp_policy

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

class SuspiciousActivityMiddleware:
    """Middleware to detect suspicious activity patterns"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check for suspicious patterns before processing
        if hasattr(request, 'client_ip'):
            self._check_suspicious_patterns(request)
        
        response = self.get_response(request)
        return response
    
    def _check_suspicious_patterns(self, request):
        """Check for suspicious activity patterns"""
        ip_address = request.client_ip
        
        # Check for rapid sequential requests
        cache_key = f"request_times_{ip_address}"
        request_times = cache.get(cache_key, [])
        
        current_time = time.time()
        request_times.append(current_time)
        
        # Keep only last 10 requests
        request_times = request_times[-10:]
        cache.set(cache_key, request_times, 300)  # 5 minute window
        
        # Analyze timing patterns
        if len(request_times) >= 5:
            intervals = [request_times[i] - request_times[i-1] 
                        for i in range(1, len(request_times))]
            
            avg_interval = sum(intervals) / len(intervals)
            
            # Too regular timing (potential bot)
            if avg_interval < 2.0:  # Less than 2 seconds between requests
                variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
                
                if variance < 0.5:  # Very low variance = robotic
                    SecurityLog.log_event(
                        event_type='suspicious_activity',
                        ip_address=ip_address,
                        description='Robotic timing pattern detected',
                        severity='medium',
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        details={
                            'avg_interval': avg_interval,
                            'variance': variance,
                            'pattern': 'robotic_timing'
                        }
                    )