# Fixed middleware.py - More effective bot detection
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
    """Enhanced middleware with proper bot detection"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit_requests = getattr(settings, 'RATE_LIMIT_REQUESTS_PER_MINUTE', 100)  # More reasonable limit
        
        # Enhanced bot patterns - more comprehensive
        self.automation_patterns = [
            re.compile(r'curl|wget', re.I),  # Command line tools
            re.compile(r'python-requests|python-urllib', re.I),  # Python requests
            re.compile(r'\bselenium\b|\bwebdriver\b', re.I),  # Selenium
            re.compile(r'puppeteer|playwright', re.I),  # Browser automation
            re.compile(r'scrapy|mechanize|beautifulsoup', re.I),  # Scraping frameworks
            re.compile(r'bot.*test|test.*bot', re.I),  # Test bots
        ]
        
        # Social media bots (legitimate but still bots)
        self.social_bot_patterns = [
            re.compile(r'facebookexternalhit|facebot|facebookcatalog', re.I),
            re.compile(r'twitterbot|linkedinbot|googlebot|bingbot', re.I),
        ]
        
        # Generic bot patterns
        self.generic_bot_patterns = [
            re.compile(r'\bbot\b|\bcrawler\b|\bspider\b|\bscraper\b', re.I),
            re.compile(r'monitoring|check|scan', re.I),
        ]
        
        # Honeypot paths
        self.honeypot_paths = [
            '/wp-admin/', '/wp-login.php', '/.env', '/config.php',
            '/phpmyadmin/', '/.git/', '/xmlrpc.php', '/admin.php'
        ]
    
    def __call__(self, request):
        request._start_time = time.time()
        client_ip = get_client_ip(request)
        request.client_ip = client_ip
        
        # Skip protection for specific paths
        if self._should_skip_protection(request):
            return self.get_response(request)
        
        # 1. IP Blacklist Check
        if self._is_ip_blacklisted(client_ip):
            return self._create_blocked_response('IP blacklisted', client_ip)
        
        # 2. Rate limiting - more reasonable
        if self._check_rate_limit(client_ip):
            return self._create_rate_limit_response()
        
        # 3. Honeypot Check
        if self._is_honeypot_access(request):
            self._handle_honeypot_trigger(client_ip, request)
            return self._create_blocked_response('Unauthorized access', client_ip)
        
        # 4. Enhanced bot detection
        bot_detection = self._detect_bot(request)
        if bot_detection['is_bot'] and bot_detection['should_block']:
            self._add_to_blacklist(client_ip, bot_detection['reason'], bot_detection['confidence'], request)
            return self._create_blocked_response(bot_detection['reason'], client_ip)
        
        # 5. Log request pattern
        self._log_request_pattern(client_ip, request)
        
        response = self.get_response(request)
        self._add_security_headers(response)
        
        return response
    
    def _should_skip_protection(self, request):
        """Skip protection for specific paths"""
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
        """Check if IP is blacklisted"""
        return IPBlacklist.is_blacklisted(ip_address)
    
    def _check_rate_limit(self, ip_address):
        """Rate limiting check"""
        cache_key = f"rate_limit_{ip_address}"
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= self.rate_limit_requests:
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
        
        cache.set(cache_key, current_requests + 1, 60)
        return False
    
    def _is_honeypot_access(self, request):
        """Check if request is accessing honeypot paths"""
        path = request.path.lower()
        return any(honeypot in path for honeypot in self.honeypot_paths)
    
    def _detect_bot(self, request):
        """Enhanced bot detection"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        client_ip = request.client_ip
        
        print(f"🔍 Middleware bot detection for {client_ip}")
        print(f"📝 User Agent: {user_agent}")
        
        detection_result = {
            'is_bot': False,
            'should_block': False,
            'confidence': 0.0,
            'reason': 'unknown',
            'methods': []
        }
        
        # 1. Check for missing user agent
        if not user_agent or len(user_agent.strip()) < 10:
            print("🚨 Missing or very short user agent")
            detection_result.update({
                'is_bot': True,
                'should_block': True,
                'confidence': 0.8,
                'reason': 'Missing or invalid user agent',
                'methods': ['missing_user_agent']
            })
            return detection_result
        
        # 2. Check for automation tools (BLOCK)
        for pattern in self.automation_patterns:
            if pattern.search(user_agent):
                print(f"🤖 Automation tool detected: {pattern.pattern}")
                detection_result.update({
                    'is_bot': True,
                    'should_block': True,
                    'confidence': 0.95,
                    'reason': 'Automation tool detected',
                    'methods': ['automation_tool']
                })
                return detection_result
        
        # 3. Check for social media bots (DON'T BLOCK, but log)
        for pattern in self.social_bot_patterns:
            if pattern.search(user_agent):
                print(f"🤖📱 Social media bot detected: {pattern.pattern}")
                detection_result.update({
                    'is_bot': True,
                    'should_block': False,  # Don't block social media bots
                    'confidence': 0.9,
                    'reason': 'Social media bot',
                    'methods': ['social_media_bot']
                })
                return detection_result
        
        # 4. Check for generic bot patterns
        for pattern in self.generic_bot_patterns:
            if pattern.search(user_agent):
                print(f"🤖 Generic bot pattern detected: {pattern.pattern}")
                detection_result.update({
                    'is_bot': True,
                    'should_block': True,
                    'confidence': 0.7,
                    'reason': 'Generic bot pattern',
                    'methods': ['generic_bot']
                })
                return detection_result
        
        # 5. Check if it looks like a browser
        browser_indicators = [
            'mozilla', 'chrome', 'safari', 'firefox', 'edge', 'opera',
            'webkit', 'gecko', 'mobile', 'android', 'iphone', 'ipad',
            'windows nt', 'macintosh', 'linux'
        ]
        
        user_agent_lower = user_agent.lower()
        browser_count = sum(1 for indicator in browser_indicators if indicator in user_agent_lower)
        
        # If it has multiple browser indicators, it's likely a real browser
        if browser_count >= 3:
            print(f"✅ Multiple browser indicators detected ({browser_count})")
            detection_result.update({
                'is_bot': False,
                'should_block': False,
                'confidence': 0.1,
                'reason': 'Browser detected',
                'methods': ['browser_detected']
            })
            return detection_result
        
        # 6. Check for version patterns (browsers have versions)
        version_patterns = [
            r'chrome/[\d.]+', r'firefox/[\d.]+', r'safari/[\d.]+', r'edge/[\d.]+'
        ]
        
        has_version = any(re.search(pattern, user_agent_lower) for pattern in version_patterns)
        
        if has_version and browser_count >= 2:
            print("✅ Browser version pattern detected")
            detection_result.update({
                'is_bot': False,
                'should_block': False,
                'confidence': 0.1,
                'reason': 'Browser with version detected',
                'methods': ['browser_version_detected']
            })
            return detection_result
        
        # 7. If user agent is too simple (potential bot)
        if len(user_agent) < 50 and browser_count < 2:
            print("🚨 Suspiciously simple user agent")
            detection_result.update({
                'is_bot': True,
                'should_block': True,
                'confidence': 0.6,
                'reason': 'Suspiciously simple user agent',
                'methods': ['simple_user_agent']
            })
            return detection_result
        
        print("✅ Passed middleware bot detection")
        return detection_result
    
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
            pass  # Don't fail requests due to logging issues
    
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