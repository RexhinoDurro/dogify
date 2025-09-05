# Fixed Bot Detection Service - Complete Human-Friendly Version
import re
import json
import hashlib
import geoip2.database
import geoip2.errors
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import Count, Q, Avg
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os
import math
import statistics
import base64

from .models import (
    BotDetection, IPBlacklist, BehavioralPattern, 
    RequestPattern, SecurityLog, ThreatIntelligence
)

class AdvancedBotDetectionService:
    """Human-friendly bot detection service - very conservative approach"""
    
    def __init__(self):
        # Only the most obvious bot patterns - very restrictive
        self.definitive_bot_patterns = [
            # Only automated tools and crawlers, NOT browsers
            {'pattern': re.compile(r'\bcurl\b|\bwget\b', re.I), 'weight': 0.95, 'category': 'command_line'},
            {'pattern': re.compile(r'python-requests|python-urllib|requests-html', re.I), 'weight': 0.95, 'category': 'python_script'},
            {'pattern': re.compile(r'\bselenium\b|\bwebdriver\b', re.I), 'weight': 0.99, 'category': 'automation'},
            {'pattern': re.compile(r'puppeteer|playwright', re.I), 'weight': 0.98, 'category': 'automation'},
            {'pattern': re.compile(r'phantomjs|phantom', re.I), 'weight': 0.97, 'category': 'headless'},
            {'pattern': re.compile(r'scrapy|mechanize|beautifulsoup', re.I), 'weight': 0.96, 'category': 'scraping'},
        ]
        
        # Facebook and social media crawlers (legitimate)
        self.social_bot_patterns = [
            {'pattern': re.compile(r'facebookexternalhit|facebot|facebookcatalog', re.I), 'weight': 0.98, 'category': 'facebook'},
            {'pattern': re.compile(r'twitterbot|twitter', re.I), 'weight': 0.95, 'category': 'twitter'},
            {'pattern': re.compile(r'linkedinbot|linkedin', re.I), 'weight': 0.95, 'category': 'linkedin'},
            {'pattern': re.compile(r'googlebot|google.*bot', re.I), 'weight': 0.92, 'category': 'google'},
            {'pattern': re.compile(r'bingbot|msnbot', re.I), 'weight': 0.90, 'category': 'bing'},
        ]
        
        # Browser indicators - if these are present, almost certainly NOT a bot
        self.browser_indicators = [
            'mozilla', 'chrome', 'safari', 'firefox', 'edge', 'opera',
            'webkit', 'gecko', 'mobile', 'android', 'iphone', 'ipad',
            'windows nt', 'macintosh', 'x11', 'linux'
        ]
        
        # Initialize components
        self.ml_model = self._load_ml_model()
        self.scaler = self._load_scaler()
        self.ensemble_models = self._load_ensemble_models()
        self.geoip_reader = self._initialize_geoip()
    
    def detect_bot(self, request_data: Dict) -> Dict:
        """
        Human-friendly bot detection - only flags obvious bots
        """
        ip_address = request_data.get('ip_address', '')
        user_agent = request_data.get('user_agent', '')
        headers = request_data.get('headers', {})
        behavioral_data = request_data.get('behavioral_data', {})
        
        print(f"🔍 Human-friendly bot detection for IP: {ip_address}")
        print(f"📝 User Agent: {user_agent[:150]}...")
        
        # Initialize results
        detection_layers = {}
        confidence_scores = []
        all_methods = []
        is_facebook_bot = False
        
        # Step 1: Check if it's a browser (if so, very unlikely to be a harmful bot)
        browser_analysis = self._analyze_browser_indicators(user_agent)
        if browser_analysis['is_browser']:
            print(f"✅ Browser detected: {browser_analysis['browser_type']}")
            
            # Even if we suspect it's a bot, trust browser patterns for humans
            if browser_analysis['browser_confidence'] >= 0.8:
                print(f"👤 High browser confidence - likely human")
                return self._create_human_result(ip_address, user_agent, browser_analysis)
        
        # Step 2: Check for social media bots (legitimate)
        social_analysis = self._analyze_social_bots(user_agent)
        if social_analysis['is_social_bot']:
            print(f"🤖📱 Social media bot detected: {social_analysis['platform']}")
            is_facebook_bot = social_analysis['platform'] == 'facebook'
            detection_layers['social_bot'] = social_analysis
            confidence_scores.append(social_analysis['confidence'] * 0.4)  # Lower weight
            all_methods.extend(social_analysis['methods'])
        
        # Step 3: Check for definitive bot patterns (automation tools, scripts)
        automation_analysis = self._analyze_automation_tools(user_agent)
        if automation_analysis['is_automation']:
            print(f"🤖 Automation tool detected: {automation_analysis['tool_type']}")
            detection_layers['automation'] = automation_analysis
            confidence_scores.append(automation_analysis['confidence'] * 0.6)
            all_methods.extend(automation_analysis['methods'])
        
        # Step 4: IP reputation (very conservative)
        ip_analysis = self._analyze_ip_conservative(ip_address)
        if ip_analysis['suspicious']:
            detection_layers['ip_analysis'] = ip_analysis
            confidence_scores.append(ip_analysis['confidence'] * 0.3)  # Low weight
            all_methods.extend(ip_analysis['methods'])
        
        # Step 5: Behavioral analysis (only for extreme cases)
        if behavioral_data:
            behavior_analysis = self._analyze_behavior_conservative(behavioral_data)
            if behavior_analysis['highly_suspicious']:
                detection_layers['behavioral'] = behavior_analysis
                confidence_scores.append(behavior_analysis['confidence'] * 0.2)  # Very low weight
                all_methods.extend(behavior_analysis['methods'])
        
        # Step 6: Request pattern analysis
        pattern_analysis = self._analyze_request_patterns_conservative(ip_address)
        if pattern_analysis['suspicious']:
            detection_layers['patterns'] = pattern_analysis
            confidence_scores.append(pattern_analysis['confidence'] * 0.2)  # Low weight
            all_methods.extend(pattern_analysis['methods'])
        
        # Calculate final confidence - be VERY conservative
        final_confidence = self._calculate_conservative_confidence(confidence_scores, detection_layers)
        
        # Only consider it a bot if we have HIGH confidence AND it's not a browser
        is_bot = (final_confidence >= 0.85 and not browser_analysis['is_browser']) or is_facebook_bot
        
        # Special handling for Facebook bots
        if is_facebook_bot:
            is_bot = True  # Facebook bots are legitimate
            final_confidence = max(final_confidence, 0.95)
        
        print(f"📊 Detection summary:")
        print(f"   - Is Bot: {is_bot}")
        print(f"   - Confidence: {final_confidence:.3f}")
        print(f"   - Is Browser: {browser_analysis['is_browser']}")
        print(f"   - Is Facebook: {is_facebook_bot}")
        print(f"   - Methods: {len(all_methods)}")
        
        # Compile result
        result = {
            'is_bot': is_bot,
            'confidence': round(final_confidence, 4),
            'methods': list(set(all_methods)),
            'geo_info': self._get_basic_geo_info(ip_address),
            'detection_layers': detection_layers,
            'analysis_timestamp': timezone.now().isoformat(),
            'risk_level': self._calculate_risk_level_conservative(final_confidence, is_facebook_bot),
            'recommended_action': self._recommend_action_conservative(final_confidence, is_bot, is_facebook_bot),
            'is_facebook_bot': is_facebook_bot,
            'browser_detected': browser_analysis['is_browser'],
            'browser_type': browser_analysis.get('browser_type', 'unknown')
        }
        
        # Log the detection
        self._log_detection_conservative(request_data, result)
        
        # Only auto-block for very high confidence non-social bots
        if is_bot and final_confidence >= 0.9 and not is_facebook_bot:
            self._execute_conservative_auto_response(ip_address, result)
        
        return result
    
    def _analyze_browser_indicators(self, user_agent: str) -> Dict:
        """Analyze if the user agent looks like a browser"""
        if not user_agent:
            return {'is_browser': False, 'browser_confidence': 0, 'browser_type': 'none'}
        
        ua_lower = user_agent.lower()
        browser_confidence = 0
        browser_type = 'unknown'
        browser_signals = []
        
        # Check for browser indicators
        if 'mozilla' in ua_lower:
            browser_confidence += 0.3
            browser_signals.append('mozilla')
        
        if 'chrome' in ua_lower:
            browser_confidence += 0.4
            browser_type = 'chrome'
            browser_signals.append('chrome')
        
        if 'safari' in ua_lower and 'chrome' not in ua_lower:
            browser_confidence += 0.4
            browser_type = 'safari'
            browser_signals.append('safari')
        
        if 'firefox' in ua_lower:
            browser_confidence += 0.4
            browser_type = 'firefox'
            browser_signals.append('firefox')
        
        if 'edge' in ua_lower:
            browser_confidence += 0.4
            browser_type = 'edge'
            browser_signals.append('edge')
        
        # Check for OS indicators
        os_indicators = ['windows nt', 'macintosh', 'mac os x', 'linux', 'android', 'iphone', 'ipad']
        for os_indicator in os_indicators:
            if os_indicator in ua_lower:
                browser_confidence += 0.2
                browser_signals.append(f'os_{os_indicator.replace(" ", "_")}')
        
        # Check for version patterns (browsers have versions)
        version_patterns = [r'chrome/[\d.]+', r'firefox/[\d.]+', r'safari/[\d.]+', r'edge/[\d.]+']
        for pattern in version_patterns:
            if re.search(pattern, ua_lower):
                browser_confidence += 0.2
                browser_signals.append('version_pattern')
        
        # Mobile indicators
        mobile_indicators = ['mobile', 'android', 'iphone', 'ipad', 'tablet']
        for mobile in mobile_indicators:
            if mobile in ua_lower:
                browser_confidence += 0.15
                browser_signals.append(f'mobile_{mobile}')
        
        is_browser = browser_confidence >= 0.5
        
        return {
            'is_browser': is_browser,
            'browser_confidence': min(browser_confidence, 1.0),
            'browser_type': browser_type,
            'signals': browser_signals
        }
    
    def _analyze_social_bots(self, user_agent: str) -> Dict:
        """Analyze for social media bots"""
        if not user_agent:
            return {'is_social_bot': False, 'confidence': 0, 'platform': 'none', 'methods': []}
        
        methods = []
        confidence = 0
        platform = 'none'
        
        for pattern_info in self.social_bot_patterns:
            if pattern_info['pattern'].search(user_agent):
                methods.append(f"social_{pattern_info['category']}")
                confidence = max(confidence, pattern_info['weight'])
                platform = pattern_info['category']
        
        return {
            'is_social_bot': confidence > 0,
            'confidence': confidence,
            'platform': platform,
            'methods': methods
        }
    
    def _analyze_automation_tools(self, user_agent: str) -> Dict:
        """Analyze for automation tools"""
        if not user_agent:
            return {'is_automation': False, 'confidence': 0, 'tool_type': 'none', 'methods': []}
        
        methods = []
        confidence = 0
        tool_type = 'none'
        
        for pattern_info in self.definitive_bot_patterns:
            if pattern_info['pattern'].search(user_agent):
                methods.append(f"automation_{pattern_info['category']}")
                confidence = max(confidence, pattern_info['weight'])
                tool_type = pattern_info['category']
        
        return {
            'is_automation': confidence > 0,
            'confidence': confidence,
            'tool_type': tool_type,
            'methods': methods
        }
    
    def _analyze_ip_conservative(self, ip_address: str) -> Dict:
        """Very conservative IP analysis"""
        if not ip_address:
            return {'suspicious': False, 'confidence': 0, 'methods': []}
        
        methods = []
        confidence = 0
        
        # Only flag if actually blacklisted
        if IPBlacklist.is_blacklisted(ip_address):
            methods.append('ip_blacklisted')
            confidence = 0.8  # Even blacklisted IPs get lower confidence for humans
        
        # Very basic datacenter check - but don't weight it heavily
        if self._is_obvious_datacenter(ip_address):
            methods.append('possible_datacenter')
            confidence = max(confidence, 0.3)  # Very low confidence
        
        return {
            'suspicious': confidence > 0.5,
            'confidence': confidence,
            'methods': methods
        }
    
    def _is_obvious_datacenter(self, ip_address: str) -> bool:
        """Only flag very obvious datacenter IPs"""
        # Very restrictive list - only major cloud providers
        obvious_datacenters = [
            '54.', '52.', '3.', '13.',  # AWS (some ranges)
            '35.', '34.',               # Google Cloud (some ranges)
            '40.', '20.',               # Azure (some ranges)
        ]
        return any(ip_address.startswith(prefix) for prefix in obvious_datacenters)
    
    def _analyze_behavior_conservative(self, behavioral_data: Dict) -> Dict:
        """Very conservative behavioral analysis - only flag extreme cases"""
        methods = []
        confidence = 0
        
        time_spent = behavioral_data.get('timeSpent', 0)
        mouse_movements = behavioral_data.get('mouseMovements', 0)
        keyboard_events = behavioral_data.get('keyboardEvents', 0)
        scroll_behavior = behavioral_data.get('scrollBehavior', 0)
        
        # Only flag if absolutely no interaction AND reasonable time spent
        if time_spent > 10000:  # More than 10 seconds
            total_interactions = mouse_movements + keyboard_events + scroll_behavior
            
            if total_interactions == 0:
                methods.append('zero_interaction')
                confidence += 0.4  # Still not very high
            
            # Flag only impossible mouse velocities
            mouse_velocity = behavioral_data.get('mouseVelocity', [])
            if mouse_velocity:
                avg_velocity = sum(mouse_velocity) / len(mouse_velocity)
                if avg_velocity > 5000:  # Impossibly fast
                    methods.append('impossible_mouse_speed')
                    confidence += 0.3
        
        return {
            'highly_suspicious': confidence >= 0.5,
            'confidence': confidence,
            'methods': methods
        }
    
    def _analyze_request_patterns_conservative(self, ip_address: str) -> Dict:
        """Very conservative request pattern analysis"""
        analysis = RequestPattern.analyze_patterns(ip_address, minutes=10)
        
        # Only flag extreme cases
        if analysis['request_count'] > 100:  # Very high threshold
            return {
                'suspicious': True,
                'confidence': 0.6,
                'methods': ['extreme_request_rate']
            }
        
        return {'suspicious': False, 'confidence': 0, 'methods': []}
    
    def _calculate_conservative_confidence(self, scores: List[float], layers: Dict) -> float:
        """Very conservative confidence calculation"""
        if not scores:
            return 0.0
        
        # Use maximum score but apply heavy dampening
        max_score = max(scores) if scores else 0.0
        
        # Apply conservative dampening
        dampening_factor = 0.7  # Reduce confidence by 30%
        final_score = max_score * dampening_factor
        
        # Additional reduction if multiple weak signals
        if len(scores) > 1 and max_score < 0.8:
            final_score *= 0.8  # Further reduction
        
        return min(final_score, 1.0)
    
    def _create_human_result(self, ip_address: str, user_agent: str, browser_analysis: Dict) -> Dict:
        """Create result for confirmed human"""
        return {
            'is_bot': False,
            'confidence': 0.1,  # Very low confidence it's a bot
            'methods': [],
            'geo_info': self._get_basic_geo_info(ip_address),
            'detection_layers': {'browser_analysis': browser_analysis},
            'analysis_timestamp': timezone.now().isoformat(),
            'risk_level': 'minimal',
            'recommended_action': 'allow',
            'is_facebook_bot': False,
            'browser_detected': True,
            'browser_type': browser_analysis.get('browser_type', 'unknown'),
            'human_confidence': browser_analysis['browser_confidence']
        }
    
    def _get_basic_geo_info(self, ip_address: str) -> Dict:
        """Get basic geographic information"""
        if not self.geoip_reader or not ip_address:
            return {}
        
        try:
            response = self.geoip_reader.city(ip_address)
            return {
                'country': response.country.iso_code,
                'country_name': response.country.name,
                'city': response.city.name,
            }
        except Exception:
            return {}
    
    def _calculate_risk_level_conservative(self, confidence: float, is_facebook_bot: bool) -> str:
        """Conservative risk level calculation"""
        if is_facebook_bot:
            return 'minimal'  # Facebook bots are legitimate
        elif confidence >= 0.9:
            return 'high'  # Only high for very confident detections
        elif confidence >= 0.7:
            return 'medium'
        else:
            return 'low'
    
    def _recommend_action_conservative(self, confidence: float, is_bot: bool, is_facebook_bot: bool) -> str:
        """Conservative action recommendations"""
        if is_facebook_bot:
            return 'allow_with_seo_content'
        elif is_bot and confidence >= 0.9:
            return 'challenge_or_block'
        elif is_bot and confidence >= 0.7:
            return 'monitor_closely'
        else:
            return 'allow'
    
    def _log_detection_conservative(self, request_data: Dict, result: Dict):
        """Conservative logging"""
        try:
            # Only log if it's actually detected as a bot with reasonable confidence
            if result['is_bot'] and result['confidence'] >= 0.6:
                detection = BotDetection.objects.create(
                    ip_address=request_data.get('ip_address', ''),
                    user_agent=request_data.get('user_agent', '')[:1000],
                    fingerprint=request_data.get('fingerprint', '')[:64],
                    is_bot=result['is_bot'],
                    confidence_score=result['confidence'],
                    url_path=request_data.get('url_path', '/')[:500],
                    http_method=request_data.get('method', 'GET')[:10],
                    referrer=request_data.get('referrer', '')[:500],
                    country_code=result['geo_info'].get('country', '')[:2],
                    city=result['geo_info'].get('city', '')[:100],
                    status='bot' if result['is_bot'] else 'clean',
                )
                
                detection.set_detection_methods(result['methods'][:20])
                detection.set_behavioral_data(request_data.get('behavioral_data', {}))
                detection.save()
                
                print(f"📝 Logged bot detection: {detection.id}")
        except Exception as e:
            print(f"❌ Failed to log detection: {e}")
    
    def _execute_conservative_auto_response(self, ip_address: str, result: Dict):
        """Very conservative auto-response"""
        try:
            # Only auto-block for very high confidence automation tools
            if result['confidence'] >= 0.95 and not result.get('is_facebook_bot', False):
                automation_detected = any('automation' in method for method in result['methods'])
                
                if automation_detected:
                    print(f"🚫 Auto-blocking automation tool: {ip_address}")
                    
                    IPBlacklist.objects.get_or_create(
                        ip_address=ip_address,
                        defaults={
                            'reason': 'Automation tool detected',
                            'confidence_score': result['confidence'],
                            'detection_method': 'conservative_auto',
                            'user_agent': '',
                            'country_code': result['geo_info'].get('country', ''),
                        }
                    )
                    
                    cache.delete(f"blacklist_{ip_address}")
        except Exception as e:
            print(f"❌ Failed to execute auto-response: {e}")
    
    def _initialize_geoip(self):
        """Initialize GeoIP database"""
        try:
            geoip_path = getattr(settings, 'GEOIP_PATH', None)
            if geoip_path and os.path.exists(os.path.join(geoip_path, 'GeoLite2-City.mmdb')):
                return geoip2.database.Reader(os.path.join(geoip_path, 'GeoLite2-City.mmdb'))
        except Exception as e:
            print(f"Failed to initialize GeoIP: {e}")
        return None
    
    def _load_ml_model(self):
        """Load ML model (disabled in conservative mode)"""
        return None
    
    def _load_scaler(self):
        """Load scaler (disabled in conservative mode)"""
        return None
    
    def _load_ensemble_models(self):
        """Load ensemble models (disabled in conservative mode)"""
        return {}
    
    def retrain_model(self, use_recent_data: bool = True, days_back: int = 30) -> Dict:
        """Model retraining disabled in conservative mode"""
        return {
            'success': False,
            'message': 'Model retraining disabled in human-friendly conservative mode',
            'reason': 'Prevents false positives and maintains stable human detection',
            'mode': 'conservative_human_friendly',
            'models_trained': 0
        }
    
    def get_statistics(self) -> Dict:
        """Get detection statistics"""
        now = timezone.now()
        last_hour = now - timedelta(hours=1)
        last_24h = now - timedelta(hours=24)
        last_week = now - timedelta(days=7)
        
        # Recent stats
        stats_1h = BotDetection.objects.filter(timestamp__gte=last_hour).aggregate(
            total_requests=Count('id'),
            bot_detections=Count('id', filter=Q(is_bot=True)),
            human_detections=Count('id', filter=Q(is_bot=False)),
            avg_confidence=Avg('confidence_score'),
            unique_ips=Count('ip_address', distinct=True)
        )
        
        stats_24h = BotDetection.objects.filter(timestamp__gte=last_24h).aggregate(
            total_requests=Count('id'),
            bot_detections=Count('id', filter=Q(is_bot=True)),
            human_detections=Count('id', filter=Q(is_bot=False)),
            avg_confidence=Avg('confidence_score'),
            unique_ips=Count('ip_address', distinct=True)
        )
        
        # Overall stats
        overall_stats = {
            'total_detections': BotDetection.objects.count(),
            'total_bots_detected': BotDetection.objects.filter(is_bot=True).count(),
            'total_humans_detected': BotDetection.objects.filter(is_bot=False).count(),
            'active_blacklist_entries': IPBlacklist.objects.filter(is_active=True).count(),
            'high_confidence_blocks': IPBlacklist.objects.filter(
                is_active=True, 
                confidence_score__gte=0.9
            ).count(),
        }
        
        # Detection method frequency (last week)
        detection_methods = {}
        recent_detections = BotDetection.objects.filter(
            timestamp__gte=last_week,
            is_bot=True
        )
        
        for detection in recent_detections:
            methods = detection.get_detection_methods()
            for method in methods:
                detection_methods[method] = detection_methods.get(method, 0) + 1
        
        # Top detection methods
        top_methods = sorted(detection_methods.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Browser detection stats
        browser_stats = {
            'chrome_detected': BotDetection.objects.filter(
                timestamp__gte=last_24h,
                user_agent__icontains='Chrome'
            ).count(),
            'firefox_detected': BotDetection.objects.filter(
                timestamp__gte=last_24h,
                user_agent__icontains='Firefox'
            ).count(),
            'safari_detected': BotDetection.objects.filter(
                timestamp__gte=last_24h,
                user_agent__icontains='Safari'
            ).count(),
        }
        
        return {
            'last_hour': stats_1h,
            'last_24_hours': stats_24h,
            'overall': overall_stats,
            'top_detection_methods': dict(top_methods),
            'browser_stats': browser_stats,
            'system_health': {
                'mode': 'conservative_human_friendly',
                'ml_models_disabled': True,
                'false_positive_protection': True,
                'browser_detection_enabled': True,
                'facebook_bot_support': True,
                'conservative_thresholds': True,
            },
            'protection_stats': {
                'humans_protected_from_false_positives': overall_stats['total_humans_detected'],
                'automation_tools_blocked': overall_stats['total_bots_detected'],
                'facebook_bots_handled': BotDetection.objects.filter(
                    is_bot=True,
                    user_agent__icontains='facebook'
                ).count(),
            },
            'generated_at': now.isoformat()
        }