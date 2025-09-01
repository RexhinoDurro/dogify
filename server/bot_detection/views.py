# views.py - Complete Django views for bot detection API
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from django.core.cache import cache
import json
import time
from datetime import datetime, timedelta
from django.utils import timezone
import hashlib
import traceback

from .bot_detection_service import BotDetectionService
from .models import BotDetection, IPBlacklist, SecurityLog, BehavioralPattern
from .middleware import get_client_ip

# Initialize bot detection service
bot_service = BotDetectionService()

class BotDetectionView(View):
    """Main bot detection endpoint"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            # Parse request data
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Request body: {request.body}")
                return JsonResponse({'error': 'Invalid JSON data', 'details': str(e)}, status=400)
            
            # Get client information
            client_ip = get_client_ip(request)
            user_agent = data.get('user_agent', request.META.get('HTTP_USER_AGENT', ''))
            
            print(f"Bot detection request from {client_ip}: {data}")
            
            # Build request data for analysis
            request_data = {
                'ip_address': client_ip,
                'user_agent': user_agent,
                'headers': dict(request.META),
                'url_path': data.get('url_path', request.path),
                'method': data.get('http_method', request.method),
                'referrer': data.get('referrer', request.META.get('HTTP_REFERER', '')),
                'timestamp': timezone.now(),
                'fingerprint': data.get('fingerprint', ''),
                'behavioral_data': data.get('behavioral', {}),
                'confidence': data.get('confidence', 0),
                'methods': data.get('methods', []),
                'response_time': time.time() - request._start_time if hasattr(request, '_start_time') else None
            }
            
            # If the frontend is reporting a bot detection, process it
            if data.get('is_bot', False) and data.get('confidence', 0) > 0.6:
                print(f"Processing frontend bot report for {client_ip}")
                # This is a bot report from the frontend
                self._handle_frontend_bot_report(request_data, data)
                
                return JsonResponse({
                    'status': 'processed',
                    'action': 'blacklisted',
                    'confidence': data.get('confidence', 0),
                    'message': 'Bot report processed successfully'
                })
            
            # Otherwise, run our own bot detection
            print(f"Running bot detection analysis for {client_ip}")
            result = bot_service.detect_bot(request_data)
            
            # If high confidence bot, block immediately
            if result['is_bot'] and result['confidence'] >= 0.8:
                print(f"High confidence bot detected: {client_ip} - {result['confidence']}")
                return HttpResponseForbidden(json.dumps({
                    'error': 'Access denied',
                    'reason': 'Bot activity detected',
                    'confidence': result['confidence'],
                    'methods': result['methods'][:3]  # Don't reveal all methods
                }), content_type='application/json')
            
            # Store behavioral data if provided
            if data.get('behavioral'):
                self._store_behavioral_data(client_ip, data['behavioral'])
            
            response_data = {
                'status': 'analyzed',
                'is_bot': result['is_bot'],
                'confidence': round(result['confidence'], 3),
                'blocked': result['is_bot'] and result['confidence'] >= 0.8,
                'warning': result['confidence'] >= 0.5,
                'session_id': self._generate_session_id(client_ip),
                'message': 'Analysis completed successfully'
            }
            
            print(f"Bot detection response for {client_ip}: {response_data}")
            return JsonResponse(response_data)
            
        except Exception as e:
            print(f"Bot detection error: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return JsonResponse({
                'error': 'Detection failed', 
                'details': str(e),
                'status': 'error'
            }, status=500)
    
    def _handle_frontend_bot_report(self, request_data, frontend_data):
        """Handle bot report from frontend"""
        try:
            ip_address = request_data['ip_address']
            print(f"Adding {ip_address} to blacklist based on frontend report")
            
            # Add to blacklist immediately
            blacklist_entry, created = IPBlacklist.objects.get_or_create(
                ip_address=ip_address,
                defaults={
                    'reason': 'Frontend bot detection',
                    'confidence_score': min(frontend_data.get('confidence', 0.9), 1.0),
                    'detection_method': ', '.join(frontend_data.get('methods', ['frontend_detection'])[:3]),
                    'user_agent': request_data['user_agent'][:500],  # Limit length
                    'fingerprint': request_data['fingerprint'][:64],  # Limit length
                    'country_code': '',
                }
            )
            
            if not created:
                print(f"Updating existing blacklist entry for {ip_address}")
                blacklist_entry.detection_count += 1
                blacklist_entry.confidence_score = max(
                    blacklist_entry.confidence_score,
                    min(frontend_data.get('confidence', 0), 1.0)
                )
                blacklist_entry.last_seen = timezone.now()
                blacklist_entry.save()
            else:
                print(f"Created new blacklist entry for {ip_address}")
            
            # Create bot detection record
            bot_detection = BotDetection.objects.create(
                ip_address=ip_address,
                user_agent=request_data['user_agent'][:500],  # TextField but let's be safe
                fingerprint=request_data['fingerprint'][:64],
                is_bot=True,
                confidence_score=min(frontend_data.get('confidence', 0.9), 1.0),
                url_path=request_data['url_path'][:500],
                http_method=request_data['method'][:10],
                referrer=request_data['referrer'][:200] if request_data['referrer'] else '',
                country_code='',
                city='',
                status='bot',
                response_time=request_data['response_time']
            )
            
            # Set JSON fields properly
            bot_detection.set_detection_methods(frontend_data.get('methods', ['frontend_detection']))
            bot_detection.set_behavioral_data(request_data.get('behavioral_data', {}))
            bot_detection.set_headers({k: str(v)[:200] for k, v in request_data.get('headers', {}).items()})  # Limit header lengths
            bot_detection.save()
            
            # Log the detection
            SecurityLog.log_event(
                event_type='bot_detected',
                ip_address=ip_address,
                description=f"Frontend reported bot with {frontend_data.get('confidence', 0):.2f} confidence",
                severity='high',
                user_agent=request_data['user_agent'][:500],
                details={
                    'methods': frontend_data.get('methods', []),
                    'confidence': frontend_data.get('confidence', 0),
                    'source': 'frontend',
                    'detection_id': str(bot_detection.id)
                }
            )
            
            # Clear cache
            cache.delete(f"blacklist_{ip_address}")
            print(f"Successfully processed frontend bot report for {ip_address}")
            
        except Exception as e:
            print(f"Failed to handle frontend bot report: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            raise  # Re-raise to be handled by the main exception handler
    
    def _store_behavioral_data(self, ip_address, behavioral_data):
        """Store behavioral data for analysis"""
        try:
            session_id = self._generate_session_id(ip_address)
            
            pattern, created = BehavioralPattern.objects.get_or_create(
                ip_address=ip_address,
                session_id=session_id,
                defaults={
                    'mouse_movements': behavioral_data.get('mouseMovements', 0),
                    'mouse_entropy': behavioral_data.get('mouseEntropy', 0.0),
                    'click_count': len(behavioral_data.get('clickPatterns', [])),
                    'scroll_events': behavioral_data.get('scrollBehavior', 0),
                    'keyboard_events': behavioral_data.get('keyboardEvents', 0),
                    'focus_events': behavioral_data.get('focusEvents', 0),
                    'time_on_page': behavioral_data.get('timeSpent', 0) / 1000,
                    'webgl_support': behavioral_data.get('webglSupport', False),
                    'screen_resolution': behavioral_data.get('screenResolution', ''),
                    'timezone_offset': behavioral_data.get('timezoneOffset', 0),
                }
            )
            
            if not created:
                # Update existing pattern
                pattern.mouse_movements = max(pattern.mouse_movements, behavioral_data.get('mouseMovements', 0))
                pattern.mouse_entropy = max(pattern.mouse_entropy, behavioral_data.get('mouseEntropy', 0.0))
                pattern.click_count += len(behavioral_data.get('clickPatterns', []))
                pattern.scroll_events += behavioral_data.get('scrollBehavior', 0)
                pattern.keyboard_events += behavioral_data.get('keyboardEvents', 0)
                pattern.time_on_page = behavioral_data.get('timeSpent', 0) / 1000
                pattern.save()
                
            print(f"Stored behavioral data for {ip_address}")
                
        except Exception as e:
            print(f"Failed to store behavioral data: {e}")
    
    def _generate_session_id(self, ip_address):
        """Generate session ID based on IP and time window"""
        # Create session ID that changes every hour
        hour_timestamp = int(time.time() // 3600)
        return hashlib.md5(f"{ip_address}_{hour_timestamp}".encode()).hexdigest()

class SecurityBotDetectionView(View):
    """High-security bot detection endpoint for immediate blocking"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            client_ip = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            print(f"Security bot detection triggered for {client_ip}")
            
            # Immediate blacklisting for this endpoint
            blacklist_entry, created = IPBlacklist.objects.get_or_create(
                ip_address=client_ip,
                defaults={
                    'reason': 'High-security bot detection triggered',
                    'confidence_score': min(data.get('confidence', 0.9), 1.0),
                    'detection_method': 'security_endpoint',
                    'user_agent': user_agent[:500],
                    'fingerprint': data.get('fingerprint', '')[:64],
                    'country_code': '',
                }
            )
            
            if not created:
                blacklist_entry.detection_count += 1
                blacklist_entry.last_seen = timezone.now()
                blacklist_entry.save()
            
            # Log critical security event
            SecurityLog.log_event(
                event_type='bot_detected',
                ip_address=client_ip,
                description='High-security bot detection triggered',
                severity='critical',
                user_agent=user_agent,
                details={
                    'endpoint': 'security',
                    'data': data,
                    'created_new_entry': created
                }
            )
            
            # Clear relevant caches
            cache.delete(f"blacklist_{client_ip}")
            
            print(f"Security blacklisting completed for {client_ip}")
            return JsonResponse({'status': 'blocked', 'action': 'blacklisted'})
            
        except Exception as e:
            print(f"Security bot detection error: {e}")
            return JsonResponse({'error': 'Security detection failed', 'details': str(e)}, status=500)

class GetClientIPView(View):
    """Endpoint to get client IP address"""
    
    def get(self, request):
        try:
            client_ip = get_client_ip(request)
            
            # Check if IP is blacklisted
            is_blacklisted = IPBlacklist.is_blacklisted(client_ip)
            
            if is_blacklisted:
                print(f"IP check: {client_ip} is blacklisted")
                return HttpResponseForbidden(json.dumps({
                    'error': 'IP blacklisted',
                    'ip': client_ip
                }), content_type='application/json')
            
            print(f"IP check: {client_ip} is clean")
            return JsonResponse({
                'ip': client_ip,
                'safe': True,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            print(f"Get IP error: {e}")
            return JsonResponse({'error': 'Failed to get IP', 'details': str(e)}, status=500)

class BotStatisticsView(View):
    """Get bot detection statistics (admin only)"""
    
    def get(self, request):
        try:
            # Simple auth check - in production, use proper authentication
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            api_key = getattr(settings, 'ADMIN_API_KEY', 'admin_key_change_me')
            
            if not auth_header == f'Bearer {api_key}':
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            print("Generating bot statistics...")
            stats = bot_service.get_statistics()
            
            # Add recent detections
            recent_detections = BotDetection.objects.filter(
                timestamp__gte=timezone.now() - timedelta(hours=24),
                is_bot=True
            ).order_by('-timestamp')[:20]
            
            stats['recent_detections'] = [
                {
                    'ip': d.ip_address,
                    'user_agent': d.user_agent[:100],
                    'confidence': d.confidence_score,
                    'methods': d.get_detection_methods(),
                    'timestamp': d.timestamp.isoformat(),
                    'country': d.country_code,
                    'status': d.status
                }
                for d in recent_detections
            ]
            
            # Add top countries
            from django.db import models
            top_countries = BotDetection.objects.filter(
                timestamp__gte=timezone.now() - timedelta(days=7),
                is_bot=True
            ).exclude(country_code='').values('country_code').annotate(
                count=models.Count('id')
            ).order_by('-count')[:10]
            
            stats['top_bot_countries'] = list(top_countries)
            
            # Add blacklist info
            stats['blacklist_info'] = {
                'total_active': IPBlacklist.objects.filter(is_active=True).count(),
                'added_today': IPBlacklist.objects.filter(
                    created_at__gte=timezone.now() - timedelta(days=1),
                    is_active=True
                ).count()
            }
            
            return JsonResponse(stats)
            
        except Exception as e:
            print(f"Statistics error: {e}")
            return JsonResponse({'error': 'Failed to get statistics', 'details': str(e)}, status=500)

class BlacklistManagementView(View):
    """Manage IP blacklist (admin only)"""
    
    def get(self, request):
        """Get blacklisted IPs"""
        try:
            # Simple auth check
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            api_key = getattr(settings, 'ADMIN_API_KEY', 'admin_key_change_me')
            
            if not auth_header == f'Bearer {api_key}':
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            page = int(request.GET.get('page', 1))
            per_page = int(request.GET.get('per_page', 50))
            
            offset = (page - 1) * per_page
            
            blacklisted = IPBlacklist.objects.filter(
                is_active=True
            ).order_by('-created_at')[offset:offset + per_page]
            
            total_count = IPBlacklist.objects.filter(is_active=True).count()
            
            return JsonResponse({
                'blacklist': [
                    {
                        'ip': entry.ip_address,
                        'reason': entry.reason,
                        'confidence': entry.confidence_score,
                        'method': entry.detection_method,
                        'country': entry.country_code,
                        'created_at': entry.created_at.isoformat(),
                        'detection_count': entry.detection_count,
                        'last_seen': entry.last_seen.isoformat()
                    }
                    for entry in blacklisted
                ],
                'total': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': (total_count + per_page - 1) // per_page
            })
            
        except Exception as e:
            print(f"Blacklist get error: {e}")
            return JsonResponse({'error': 'Failed to get blacklist', 'details': str(e)}, status=500)
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def delete(self, request):
        """Remove IP from blacklist"""
        try:
            # Simple auth check
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            api_key = getattr(settings, 'ADMIN_API_KEY', 'admin_key_change_me')
            
            if not auth_header == f'Bearer {api_key}':
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            data = json.loads(request.body)
            ip_address = data.get('ip_address')
            
            if not ip_address:
                return JsonResponse({'error': 'IP address required'}, status=400)
            
            # Soft delete - mark as inactive
            updated = IPBlacklist.objects.filter(
                ip_address=ip_address,
                is_active=True
            ).update(is_active=False)
            
            if updated:
                # Clear cache
                cache.delete(f"blacklist_{ip_address}")
                
                # Log the action
                SecurityLog.log_event(
                    event_type='ip_unblocked',
                    ip_address=ip_address,
                    description=f'IP removed from blacklist by admin API',
                    severity='medium',
                    details={'admin_action': True}
                )
                
                print(f"Removed {ip_address} from blacklist")
                return JsonResponse({'status': 'removed', 'ip': ip_address})
            else:
                return JsonResponse({'error': 'IP not found in blacklist'}, status=404)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Blacklist delete error: {e}")
            return JsonResponse({'error': 'Failed to remove IP', 'details': str(e)}, status=500)

class RetrainModelView(View):
    """Retrain ML model (admin only)"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            # Simple auth check
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            api_key = getattr(settings, 'ADMIN_API_KEY', 'admin_key_change_me')
            
            if not auth_header == f'Bearer {api_key}':
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            print("Starting model retraining...")
            success = bot_service.retrain_model()
            
            if success:
                SecurityLog.log_event(
                    event_type='model_retrained',
                    ip_address=get_client_ip(request),
                    description='ML model retrained via admin API',
                    severity='low',
                    details={'admin_action': True}
                )
                
                print("Model retraining completed successfully")
                return JsonResponse({
                    'status': 'success',
                    'message': 'Model retrained successfully'
                })
            else:
                print("Model retraining failed")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Failed to retrain model'
                }, status=500)
                
        except Exception as e:
            print(f"Model retrain error: {e}")
            return JsonResponse({'error': 'Retrain failed', 'details': str(e)}, status=500)

@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint"""
    try:
        # Test database connection
        db_healthy = True
        try:
            BotDetection.objects.count()
        except Exception as e:
            print(f"Database health check failed: {e}")
            db_healthy = False
        
        # Test cache
        cache_healthy = True
        try:
            cache.set('health_check', 'ok', 10)
            cache_healthy = cache.get('health_check') == 'ok'
        except Exception as e:
            print(f"Cache health check failed: {e}")
            cache_healthy = False
        
        status = 'healthy' if db_healthy and cache_healthy else 'degraded'
        
        return JsonResponse({
            'status': status,
            'timestamp': timezone.now().isoformat(),
            'version': '1.0.0',
            'database': 'healthy' if db_healthy else 'unhealthy',
            'cache': 'healthy' if cache_healthy else 'unhealthy',
            'bot_service': 'available' if bot_service else 'unavailable'
        }, status=200 if status == 'healthy' else 503)
        
    except Exception as e:
        print(f"Health check error: {e}")
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def webhook_threat_intel(request):
    """Webhook to receive threat intelligence updates"""
    try:
        # Verify webhook secret (implement your security)
        webhook_secret = getattr(settings, 'THREAT_INTEL_WEBHOOK_SECRET', None)
        if webhook_secret:
            # Implement signature verification here
            provided_signature = request.META.get('HTTP_X_SIGNATURE', '')
            # Add signature verification logic
        
        data = json.loads(request.body)
        print(f"Received threat intelligence update: {len(data.get('threats', []))} threats")
        
        # Process threat intelligence data
        processed_count = 0
        for threat in data.get('threats', []):
            try:
                from .models import ThreatIntelligence
                threat_intel, created = ThreatIntelligence.objects.update_or_create(
                    ip_address=threat['ip'],
                    threat_type=threat.get('type', 'malicious_ip'),
                    defaults={
                        'confidence': min(threat.get('confidence', 0.8), 1.0),
                        'source': threat.get('source', 'webhook'),
                        'description': threat.get('description', ''),
                        'first_seen': timezone.now(),
                        'is_active': True
                    }
                )
                processed_count += 1
                if created:
                    print(f"Added new threat intel for {threat['ip']}")
                else:
                    print(f"Updated threat intel for {threat['ip']}")
                    
            except Exception as e:
                print(f"Failed to process threat {threat}: {e}")
        
        return JsonResponse({
            'status': 'processed', 
            'received': len(data.get('threats', [])),
            'processed': processed_count
        })
        
    except Exception as e:
        print(f"Threat intel webhook error: {e}")
        return JsonResponse({'error': 'Processing failed', 'details': str(e)}, status=500)