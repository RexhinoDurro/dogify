# models.py - Django models for bot detection and tracking
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import json
import uuid
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models import Q, Count, Avg
from datetime import timedelta
from django.core.cache import cache

class IPBlacklist(models.Model):
    """Model to store blacklisted IPs with detailed information"""
    ip_address = models.GenericIPAddressField(unique=True, db_index=True)
    reason = models.CharField(max_length=255)
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    detection_method = models.CharField(max_length=100)
    user_agent = models.TextField(blank=True)
    fingerprint = models.CharField(max_length=64, blank=True)
    country_code = models.CharField(max_length=2, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Additional metadata
    detection_count = models.PositiveIntegerField(default=1)
    last_seen = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ip_blacklist'
        indexes = [
            models.Index(fields=['ip_address', 'is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['confidence_score']),
        ]
    
    def __str__(self):
        return f"{self.ip_address} - {self.reason}"
    
    @classmethod
    def is_blacklisted(cls, ip_address):
        """Check if an IP is blacklisted"""
        cache_key = f"blacklist_{ip_address}"
        result = cache.get(cache_key)
        if result is None:
            result = cls.objects.filter(
                ip_address=ip_address, 
                is_active=True
            ).exists()
            cache.set(cache_key, result, 300)  # Cache for 5 minutes
        return result

class BotDetection(models.Model):
    """Model to store all bot detection attempts"""
    DETECTION_STATUS_CHOICES = [
        ('clean', 'Clean'),
        ('suspicious', 'Suspicious'),
        ('bot', 'Bot Detected'),
        ('blocked', 'Blocked'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip_address = models.GenericIPAddressField(db_index=True)
    user_agent = models.TextField()
    fingerprint = models.CharField(max_length=64)
    
    # Detection results
    is_bot = models.BooleanField(default=False)
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    detection_methods = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True
    )
    
    # Request details
    url_path = models.CharField(max_length=500)
    http_method = models.CharField(max_length=10)
    referrer = models.URLField(blank=True)
    
    # Geographic info
    country_code = models.CharField(max_length=2, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Behavioral data
    behavioral_data = JSONField(default=dict, blank=True)
    
    # Technical details
    headers = JSONField(default=dict, blank=True)
    
    # Timing
    timestamp = models.DateTimeField(auto_now_add=True)
    response_time = models.FloatField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20, 
        choices=DETECTION_STATUS_CHOICES,
        default='clean'
    )
    
    class Meta:
        db_table = 'bot_detections'
        indexes = [
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['is_bot', 'timestamp']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.ip_address} - {self.status} ({self.confidence_score:.2f})"
    
    @classmethod
    def get_ip_stats(cls, ip_address, hours=24):
        """Get statistics for a specific IP"""
        since = timezone.now() - timedelta(hours=hours)
        stats = cls.objects.filter(
            ip_address=ip_address,
            timestamp__gte=since
        ).aggregate(
            total_requests=Count('id'),
            bot_detections=Count('id', filter=Q(is_bot=True)),
            avg_confidence=Avg('confidence_score'),
            suspicious_count=Count('id', filter=Q(status='suspicious'))
        )
        return stats

class BehavioralPattern(models.Model):
    """Model to track behavioral patterns for ML analysis"""
    ip_address = models.GenericIPAddressField(db_index=True)
    session_id = models.CharField(max_length=64)
    
    # Mouse behavior
    mouse_movements = models.IntegerField(default=0)
    mouse_entropy = models.FloatField(default=0.0)
    
    # Click patterns
    click_count = models.IntegerField(default=0)
    avg_click_interval = models.FloatField(default=0.0)
    click_timing_variance = models.FloatField(default=0.0)
    
    # Scroll behavior
    scroll_events = models.IntegerField(default=0)
    scroll_patterns = ArrayField(
        models.FloatField(),
        default=list,
        blank=True
    )
    
    # Keyboard behavior
    keyboard_events = models.IntegerField(default=0)
    keyboard_rhythm = ArrayField(
        models.FloatField(),
        default=list,
        blank=True
    )
    
    # Focus patterns
    focus_events = models.IntegerField(default=0)
    page_visibility_changes = models.IntegerField(default=0)
    
    # Time tracking
    time_on_page = models.FloatField(default=0.0)  # seconds
    session_duration = models.FloatField(default=0.0)  # seconds
    
    # Browser features
    webgl_support = models.BooleanField(default=False)
    canvas_fingerprint = models.TextField(blank=True)
    audio_fingerprint = models.TextField(blank=True)
    font_count = models.IntegerField(default=0)
    plugin_count = models.IntegerField(default=0)
    
    # Device info
    screen_resolution = models.CharField(max_length=20, blank=True)
    timezone_offset = models.IntegerField(default=0)
    language_count = models.IntegerField(default=1)
    hardware_concurrency = models.IntegerField(default=1)
    device_memory = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'behavioral_patterns'
        indexes = [
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['session_id']),
        ]
    
    def calculate_human_score(self):
        """Calculate how human-like the behavior is"""
        score = 0.0
        
        # Mouse movement analysis
        if self.mouse_movements > 10:
            score += 0.2
        if self.mouse_entropy > 5.0:
            score += 0.1
            
        # Click pattern analysis
        if self.click_count > 0:
            if 100 <= self.avg_click_interval <= 2000:  # Human-like timing
                score += 0.15
            if self.click_timing_variance > 1000:  # Natural variance
                score += 0.1
        
        # Scroll behavior
        if self.scroll_events > 0:
            score += 0.1
            
        # Keyboard events
        if self.keyboard_events > 0:
            score += 0.1
            
        # Browser features
        if self.webgl_support:
            score += 0.1
        if self.font_count > 5:
            score += 0.05
        if self.plugin_count > 0:
            score += 0.05
            
        # Time spent
        if self.time_on_page > 10:  # More than 10 seconds
            score += 0.1
            
        return min(score, 1.0)

class RequestPattern(models.Model):
    """Model to track request patterns for bot detection"""
    ip_address = models.GenericIPAddressField(db_index=True)
    endpoint = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)
    response_code = models.IntegerField()
    response_time = models.FloatField()
    user_agent_hash = models.CharField(max_length=64)
    
    class Meta:
        db_table = 'request_patterns'
        indexes = [
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['endpoint']),
        ]
    
    @classmethod
    def analyze_patterns(cls, ip_address, minutes=5):
        """Analyze request patterns for bot-like behavior"""
        since = timezone.now() - timedelta(minutes=minutes)
        patterns = cls.objects.filter(
            ip_address=ip_address,
            timestamp__gte=since
        ).order_by('timestamp')
        
        if not patterns:
            return {'suspicious': False, 'reasons': []}
        
        reasons = []
        
        # Check request frequency
        total_requests = patterns.count()
        if total_requests > 50:  # More than 50 requests in 5 minutes
            reasons.append('High request frequency')
        
        # Check for scanning behavior
        unique_endpoints = patterns.values_list('endpoint', flat=True).distinct().count()
        if unique_endpoints > 20 and total_requests > 30:
            reasons.append('Scanning behavior detected')
        
        # Check timing patterns
        timestamps = list(patterns.values_list('timestamp', flat=True))
        if len(timestamps) >= 10:
            intervals = [(timestamps[i] - timestamps[i-1]).total_seconds() 
                        for i in range(1, len(timestamps))]
            
            avg_interval = sum(intervals) / len(intervals)
            variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
            
            if variance < 1.0 and avg_interval < 5.0:  # Too regular
                reasons.append('Robotic timing patterns')
        
        return {
            'suspicious': len(reasons) > 0,
            'reasons': reasons,
            'request_count': total_requests,
            'unique_endpoints': unique_endpoints
        }

class ThreatIntelligence(models.Model):
    """Model to store threat intelligence data"""
    THREAT_TYPES = [
        ('malicious_ip', 'Malicious IP'),
        ('bot_network', 'Bot Network'),
        ('proxy', 'Proxy/VPN'),
        ('datacenter', 'Datacenter IP'),
    ]
    
    ip_address = models.GenericIPAddressField(db_index=True)
    threat_type = models.CharField(max_length=20, choices=THREAT_TYPES)
    confidence = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    source = models.CharField(max_length=100)  # Source of intel
    description = models.TextField(blank=True)
    first_seen = models.DateTimeField()
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'threat_intelligence'
        unique_together = ['ip_address', 'threat_type']
        indexes = [
            models.Index(fields=['ip_address', 'is_active']),
            models.Index(fields=['threat_type']),
        ]

class SecurityLog(models.Model):
    """Model to log all security events"""
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    EVENT_TYPES = [
        ('bot_detected', 'Bot Detected'),
        ('ip_blocked', 'IP Blocked'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('rate_limit_exceeded', 'Rate Limit Exceeded'),
        ('honeypot_triggered', 'Honeypot Triggered'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    description = models.TextField()
    details = JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'security_logs'
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['severity', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
    
    @classmethod
    def log_event(cls, event_type, ip_address, description, severity='medium', **kwargs):
        """Log a security event"""
        return cls.objects.create(
            event_type=event_type,
            severity=severity,
            ip_address=ip_address,
            description=description,
            user_agent=kwargs.get('user_agent', ''),
            details=kwargs.get('details', {})
        )