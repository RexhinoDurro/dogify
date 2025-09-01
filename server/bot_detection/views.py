# views.py - Django views for bot detection API
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
            data = json.loads(request.body)
            
            # Get client information
            client_ip = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Build request data for analysis
            request_data = {
                'ip_address': client_ip,
                'user_agent': user_agent,
                'headers': dict(request.META),
                'url_path': request.path,
                'method': request.method,
                'referrer': request.META.get('HTTP_REFERER', ''),
                'timestamp': timezone.now(),
                'fingerprint': data.get('fingerprint', ''),
                'behavioral_data': data.get('behavioral', {}),
                'confidence': data.get('confidence', 0),
                'methods': data.get('methods', []),
                'response_time': time.time() - request._start_time if hasattr(request, '_start_time') else None
            }
            
            # Run bot detection
            result = bot_service.detect_bot(request_data)
            
            # If high confidence bot, block immediately
            if result['is_bot'] and result['confidence'] >= 0.8:
                return HttpResponseForbidden(json.dumps({
                    'error': 'Access denied',
                    'reason': 'Bot activity detected',
                    'confidence': result['confidence'],
                    'methods': result['methods'][:3]  # Don't reveal all methods
                }), content_type='application/json')
            
            # Store behavioral data if provided
            if data.get('behavioral'):
                self._store_behavioral_data(client_ip, data['behavioral'])
            
            return JsonResponse({
                'status': 'analyzed',
                'is_bot': result['is_bot'],
                'confidence': round(result['confidence'], 3),
                'blocked': result['is_bot'] and result['confidence'] >= 0.8,
                'warning': result['confidence'] >= 0.5,
                'session_id': self._generate_session_id(client_ip),
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Detection failed'}, status=500)
    
    def _store_behavioral_data(self, ip_address, behavioral_data):
        """Store behavioral data for analysis"""
        try:
            session_id = self._generate_session_id(ip_address)
            
            pattern, created = BehavioralPattern.objects.get_or_create(
                ip_address=ip_address,
                session_id=session_id,
                defaults={
                    'mouse_movements': behavioral_data.get('mouseMovements', 0),
                    'mouse_entropy': behavioral_data.get('mouseEntropy', 0),
                    'click_count': len(behavioral_data.get('clickPatterns', [])),
                    'scroll_events': behavioral_data.get('scrollBehavior', 0),
                    'keyboard_events': behavioral_data.get('keyboardEvents', 0),
                    'focus_events': behavioral_data.get('focusEvents', 0),
                    'time_on_page': behavioral_data.get('timeSpent', 0) / 1000,
                }
            )
            
            if not created:
                # Update existing pattern
                pattern.mouse_movements = max(pattern.mouse_movements, behavioral_data.get('mouseMovements', 0))
                pattern.mouse_entropy = max(pattern.mouse_entropy, behavioral_data.get('mouseEntropy', 0))
                pattern.click_count += len(behavioral_data.get('clickPatterns', []))
                pattern.scroll_events += behavioral_data.get('scrollBehavior', 0)
                pattern.keyboard_events += behavioral_data.get('keyboardEvents', 0)
                pattern.time_on_page = behavioral_data.get('timeSpent', 0) / 1000
                pattern.save()
                
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
            
            # Immediate blacklisting for this endpoint
            IPBlacklist.objects.get_or_create(
                ip_address=client_ip,
                defaults={
                    'reason': 'High-security bot detection triggered',
                    'confidence_score': data.get('confidence', 0.9),
                    'detection_method': 'security_endpoint',
                    'user_agent': user_agent,
                    'fingerprint': data.get('fingerprint', ''),
                }
            )
            
            # Log critical security event
            SecurityLog.log_event(
                event_type='bot_detected',
                ip_address=client_ip,
                description='High-security bot detection triggered',
                severity='critical',
                user_agent=user_agent,
                details=data
            )
            
            # Clear relevant caches
            cache.delete(f"blacklist_{client_ip}")
            
            return JsonResponse({'status': 'blocked', 'action': 'blacklisted'})
            
        except Exception as e:
            return JsonResponse({'error': 'Security detection failed'}, status=500)

class GetClientIPView(View):
    """Endpoint to get client IP address"""
    
    def get(self, request):
        client_ip = get_client_ip(request)
        
        # Check if IP is blacklisted
        is_blacklisted = IPBlacklist.is_blacklisted(client_ip)
        
        if is_blacklisted:
            return HttpResponseForbidden(json.dumps({
                'error': 'IP blacklisted'
            }), content_type='application/json')
        
        return JsonResponse({
            'ip': client_ip,
            'safe': True
        })

class BotStatisticsView(View):
    """Get bot detection statistics (admin only)"""
    
    def get(self, request):
        # In production, add proper authentication here
        if not request.user.is_authenticated or not request.user.is_staff:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
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
                'methods': d.detection_methods,
                'timestamp': d.timestamp.isoformat(),
                'country': d.country_code
            }
            for d in recent_detections
        ]
        
        # Add top countries
        from django.db import models
        top_countries = BotDetection.objects.filter(
            timestamp__gte=timezone.now() - timedelta(days=7),
            is_bot=True
        ).values('country_code').annotate(
            count=models.Count('id')
        ).order_by('-count')[:10]
        
        stats['top_bot_countries'] = list(top_countries)
        
        return JsonResponse(stats)

class BlacklistManagementView(View):
    """Manage IP blacklist (admin only)"""
    
    def get(self, request):
        """Get blacklisted IPs"""
        if not request.user.is_authenticated or not request.user.is_staff:
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
    
    def delete(self, request):
        """Remove IP from blacklist"""
        if not request.user.is_authenticated or not request.user.is_staff:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
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
                    description=f'IP removed from blacklist by admin: {request.user.username}',
                    severity='medium',
                    details={'admin_user': request.user.username}
                )
                
                return JsonResponse({'status': 'removed', 'ip': ip_address})
            else:
                return JsonResponse({'error': 'IP not found in blacklist'}, status=404)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class RetrainModelView(View):
    """Retrain ML model (admin only)"""
    
    def post(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            success = bot_service.retrain_model()
            
            if success:
                SecurityLog.log_event(
                    event_type='model_retrained',
                    ip_address=get_client_ip(request),
                    description=f'ML model retrained by admin: {request.user.username}',
                    severity='low',
                    details={'admin_user': request.user.username}
                )
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Model retrained successfully'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Failed to retrain model'
                }, status=500)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    })

@csrf_exempt
@require_http_methods(["POST"])
def webhook_threat_intel(request):
    """Webhook to receive threat intelligence updates"""
    try:
        # Verify webhook signature (implement your security)
        webhook_secret = getattr(settings, 'THREAT_INTEL_WEBHOOK_SECRET', None)
        if webhook_secret:
            # Implement signature verification here
            pass
        
        data = json.loads(request.body)
        
        # Process threat intelligence data
        for threat in data.get('threats', []):
            from .models import ThreatIntelligence
            ThreatIntelligence.objects.update_or_create(
                ip_address=threat['ip'],
                threat_type=threat['type'],
                defaults={
                    'confidence': threat.get('confidence', 0.8),
                    'source': threat.get('source', 'webhook'),
                    'description': threat.get('description', ''),
                    'first_seen': timezone.now(),
                    'is_active': True
                }
            )
        
        return JsonResponse({'status': 'processed', 'count': len(data.get('threats', []))})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)