# Fixed Bot Detection Service - More Accurate Bot Detection
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
    """Fixed bot detection service with proper thresholds"""
    
    def __init__(self):
        # Enhanced bot patterns - more comprehensive detection
        self.automation_patterns = [
            {'pattern': re.compile(r'\bcurl\b|\bwget\b', re.I), 'weight': 0.99, 'category': 'command_line'},
            {'pattern': re.compile(r'python-requests|python-urllib|requests-html', re.I), 'weight': 0.95, 'category': 'python_script'},
            {'pattern': re.compile(r'\bselenium\b|\bwebdriver\b', re.I), 'weight': 0.99, 'category': 'automation'},
            {'pattern': re.compile(r'puppeteer|playwright', re.I), 'weight': 0.98, 'category': 'automation'},
            {'pattern': re.compile(r'phantomjs|phantom', re.I), 'weight': 0.97, 'category': 'headless'},
            {'pattern': re.compile(r'scrapy|mechanize|beautifulsoup', re.I), 'weight': 0.96, 'category': 'scraping'},
            {'pattern': re.compile(r'bot\w*test|test\w*bot|botify', re.I), 'weight': 0.98, 'category': 'test_bot'},
        ]
        
        # Social media crawlers (legitimate but still bots)
        self.social_bot_patterns = [
            {'pattern': re.compile(r'facebookexternalhit|facebot|facebookcatalog', re.I), 'weight': 0.98, 'category': 'facebook'},
            {'pattern': re.compile(r'twitterbot|twitter', re.I), 'weight': 0.95, 'category': 'twitter'},
            {'pattern': re.compile(r'linkedinbot|linkedin', re.I), 'weight': 0.95, 'category': 'linkedin'},
            {'pattern': re.compile(r'googlebot|google.*bot', re.I), 'weight': 0.92, 'category': 'google'},
            {'pattern': re.compile(r'bingbot|msnbot', re.I), 'weight': 0.90, 'category': 'bing'},
        ]
        
        # Generic bot patterns
        self.generic_bot_patterns = [
            {'pattern': re.compile(r'\bbot\b|\bcrawler\b|\bspider\b|\bscraper\b', re.I), 'weight': 0.85, 'category': 'generic_bot'},
            {'pattern': re.compile(r'monitoring|check|test|scan', re.I), 'weight': 0.70, 'category': 'monitoring'},
        ]
        
        # Browser indicators - must be comprehensive
        self.browser_indicators = [
            'mozilla', 'chrome', 'safari', 'firefox', 'edge', 'opera',
            'webkit', 'gecko', 'mobile', 'android', 'iphone', 'ipad',
            'windows nt', 'macintosh', 'x11', 'linux', 'trident', 'msie'
        ]
        
        # Initialize components
        self.ml_model = self._load_ml_model()
        self.scaler = self._load_scaler()
        self.ensemble_models = self._load_ensemble_models()
        self.geoip_reader = self._initialize_geoip()
    
    def detect_bot(self, request_data: Dict) -> Dict:
        """
        Enhanced bot detection with proper thresholds
        """
        ip_address = request_data.get('ip_address', '')
        user_agent = request_data.get('user_agent', '')
        headers = request_data.get('headers', {})
        behavioral_data = request_data.get('behavioral_data', {})
        
        print(f"🔍 Enhanced bot detection for IP: {ip_address}")
        print(f"📝 User Agent: {user_agent[:150]}...")
        
        # Initialize results
        detection_layers = {}
        confidence_scores = []
        all_methods = []
        is_facebook_bot = False
        
        # Step 1: Check for automation tools (highest priority)
        automation_analysis = self._analyze_automation_tools(user_agent)
        if automation_analysis['is_automation']:
            print(f"🤖 Automation tool detected: {automation_analysis['tool_type']}")
            detection_layers['automation'] = automation_analysis
            confidence_scores.append(automation_analysis['confidence'])
            all_methods.extend(automation_analysis['methods'])
        
        # Step 2: Check for social media bots
        social_analysis = self._analyze_social_bots(user_agent)
        if social_analysis['is_social_bot']:
            print(f"🤖📱 Social media bot detected: {social_analysis['platform']}")
            is_facebook_bot = social_analysis['platform'] == 'facebook'
            detection_layers['social_bot'] = social_analysis
            confidence_scores.append(social_analysis['confidence'] * 0.8)  # Social bots are legitimate
            all_methods.extend(social_analysis['methods'])
        
        # Step 3: Generic bot pattern analysis
        generic_analysis = self._analyze_generic_bots(user_agent)
        if generic_analysis['is_generic_bot']:
            print(f"🤖 Generic bot detected: {generic_analysis['bot_type']}")
            detection_layers['generic_bot'] = generic_analysis
            confidence_scores.append(generic_analysis['confidence'] * 0.7)
            all_methods.extend(generic_analysis['methods'])
        
        # Step 4: Browser analysis (important for excluding humans)
        browser_analysis = self._analyze_browser_indicators(user_agent)
        detection_layers['browser_analysis'] = browser_analysis
        
        # If it looks like a browser, reduce bot confidence significantly
        if browser_analysis['is_browser'] and browser_analysis['browser_confidence'] >= 0.7:
            print(f"✅ Strong browser indicators detected: {browser_analysis['browser_type']}")
            # Reduce all confidence scores for browser-like user agents
            confidence_scores = [score * 0.3 for score in confidence_scores]
            all_methods.append('browser_detected_confidence_reduced')
        
        # Step 5: Missing/suspicious user agent
        if not user_agent or len(user_agent.strip()) < 10:
            print(f"🚨 Missing or very short user agent")
            confidence_scores.append(0.8)
            all_methods.append('missing_or_short_user_agent')
        
        # Step 6: IP reputation analysis
        ip_analysis = self._analyze_ip_reputation(ip_address)
        if ip_analysis['suspicious']:
            detection_layers['ip_analysis'] = ip_analysis
            confidence_scores.append(ip_analysis['confidence'] * 0.4)
            all_methods.extend(ip_analysis['methods'])
        
        # Step 7: Behavioral analysis (if data available)
        if behavioral_data:
            behavior_analysis = self._analyze_behavior_patterns(behavioral_data)
            if behavior_analysis['suspicious']:
                detection_layers['behavioral'] = behavior_analysis
                confidence_scores.append(behavior_analysis['confidence'] * 0.6)
                all_methods.extend(behavior_analysis['methods'])
        
        # Step 8: Request pattern analysis
        pattern_analysis = self._analyze_request_patterns(ip_address)
        if pattern_analysis['suspicious']:
            detection_layers['patterns'] = pattern_analysis
            confidence_scores.append(pattern_analysis['confidence'] * 0.5)
            all_methods.extend(pattern_analysis['methods'])
        
        # Calculate final confidence with proper weights
        final_confidence = self._calculate_weighted_confidence(confidence_scores, detection_layers)
        
        # Determine if it's a bot with proper thresholds
        is_bot = self._determine_bot_status(final_confidence, detection_layers, is_facebook_bot)
        
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
            'risk_level': self._calculate_risk_level(final_confidence, is_facebook_bot),
            'recommended_action': self._recommend_action(final_confidence, is_bot, is_facebook_bot),
            'is_facebook_bot': is_facebook_bot,
            'browser_detected': browser_analysis['is_browser'],
            'browser_type': browser_analysis.get('browser_type', 'unknown')
        }
        
        # Log the detection
        self._log_detection(request_data, result)
        
        # Auto-response for high confidence bots
        if is_bot and final_confidence >= 0.7:
            self._execute_auto_response(ip_address, result)
        
        return result
    
    def _analyze_automation_tools(self, user_agent: str) -> Dict:
        """Analyze for automation tools"""
        if not user_agent:
            return {'is_automation': False, 'confidence': 0, 'tool_type': 'none', 'methods': []}
        
        methods = []
        confidence = 0
        tool_type = 'none'
        
        for pattern_info in self.automation_patterns:
            if pattern_info['pattern'].search(user_agent):
                methods.append(f"automation_{pattern_info['category']}")
                confidence = max(confidence, pattern_info['weight'])
                tool_type = pattern_info['category']
                print(f"🔍 Automation pattern matched: {pattern_info['category']}")
        
        return {
            'is_automation': confidence > 0,
            'confidence': confidence,
            'tool_type': tool_type,
            'methods': methods
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
                print(f"🔍 Social bot pattern matched: {pattern_info['category']}")
        
        return {
            'is_social_bot': confidence > 0,
            'confidence': confidence,
            'platform': platform,
            'methods': methods
        }
    
    def _analyze_generic_bots(self, user_agent: str) -> Dict:
        """Analyze for generic bot patterns"""
        if not user_agent:
            return {'is_generic_bot': False, 'confidence': 0, 'bot_type': 'none', 'methods': []}
        
        methods = []
        confidence = 0
        bot_type = 'none'
        
        for pattern_info in self.generic_bot_patterns:
            if pattern_info['pattern'].search(user_agent):
                methods.append(f"generic_{pattern_info['category']}")
                confidence = max(confidence, pattern_info['weight'])
                bot_type = pattern_info['category']
                print(f"🔍 Generic bot pattern matched: {pattern_info['category']}")
        
        return {
            'is_generic_bot': confidence > 0,
            'confidence': confidence,
            'bot_type': bot_type,
            'methods': methods
        }
    
    def _analyze_browser_indicators(self, user_agent: str) -> Dict:
        """Fixed browser analysis"""
        if not user_agent:
            return {'is_browser': False, 'browser_confidence': 0, 'browser_type': 'none'}
        
        ua_lower = user_agent.lower()
        browser_confidence = 0
        browser_type = 'unknown'
        browser_signals = []
        
        # Check for specific browsers
        if 'chrome' in ua_lower and 'webkit' in ua_lower:
            browser_confidence += 0.4
            browser_type = 'chrome'
            browser_signals.append('chrome')
        
        if 'firefox' in ua_lower and 'gecko' in ua_lower:
            browser_confidence += 0.4
            browser_type = 'firefox'
            browser_signals.append('firefox')
        
        if 'safari' in ua_lower and 'webkit' in ua_lower and 'chrome' not in ua_lower:
            browser_confidence += 0.4
            browser_type = 'safari'
            browser_signals.append('safari')
        
        if 'edge' in ua_lower or 'edg/' in ua_lower:
            browser_confidence += 0.4
            browser_type = 'edge'
            browser_signals.append('edge')
        
        # Mozilla indicator (most browsers have this)
        if 'mozilla' in ua_lower:
            browser_confidence += 0.2
            browser_signals.append('mozilla')
        
        # Operating system indicators
        os_indicators = ['windows nt', 'macintosh', 'mac os x', 'linux', 'android', 'iphone', 'ipad']
        for os_indicator in os_indicators:
            if os_indicator in ua_lower:
                browser_confidence += 0.2
                browser_signals.append(f'os_{os_indicator.replace(" ", "_")}')
        
        # Version patterns (browsers have version numbers)
        version_patterns = [r'chrome/[\d.]+', r'firefox/[\d.]+', r'safari/[\d.]+', r'edge?/[\d.]+']
        for pattern in version_patterns:
            if re.search(pattern, ua_lower):
                browser_confidence += 0.3
                browser_signals.append('version_pattern')
                break
        
        # Mobile indicators
        mobile_indicators = ['mobile', 'android', 'iphone', 'ipad', 'tablet']
        for mobile in mobile_indicators:
            if mobile in ua_lower:
                browser_confidence += 0.2
                browser_signals.append(f'mobile_{mobile}')
        
        # Complexity check - real browsers have complex user agents
        if len(user_agent) > 50 and '(' in user_agent and ')' in user_agent:
            browser_confidence += 0.2
            browser_signals.append('complex_structure')
        
        is_browser = browser_confidence >= 0.6  # Adjusted threshold
        
        return {
            'is_browser': is_browser,
            'browser_confidence': min(browser_confidence, 1.0),
            'browser_type': browser_type,
            'signals': browser_signals
        }
    
    def _analyze_ip_reputation(self, ip_address: str) -> Dict:
        """Analyze IP reputation"""
        if not ip_address:
            return {'suspicious': False, 'confidence': 0, 'methods': []}
        
        methods = []
        confidence = 0
        
        # Check blacklist
        if IPBlacklist.is_blacklisted(ip_address):
            methods.append('ip_blacklisted')
            confidence = 0.9
        
        # Check for obvious datacenter IPs
        if self._is_datacenter_ip(ip_address):
            methods.append('datacenter_ip')
            confidence = max(confidence, 0.6)
        
        return {
            'suspicious': confidence > 0.3,
            'confidence': confidence,
            'methods': methods
        }
    
    def _is_datacenter_ip(self, ip_address: str) -> bool:
        """Check if IP is from a datacenter"""
        # Expanded datacenter detection
        datacenter_ranges = [
            '54.', '52.', '3.', '13.', '34.', '35.',  # AWS, Google
            '40.', '20.', '104.', '168.',             # Azure, others
            '159.', '178.', '185.', '188.',           # VPS providers
            '167.', '172.', '173.', '198.',           # Hosting providers
        ]
        return any(ip_address.startswith(prefix) for prefix in datacenter_ranges)
    
    def _analyze_behavior_patterns(self, behavioral_data: Dict) -> Dict:
        """Analyze behavioral patterns for bot indicators"""
        methods = []
        confidence = 0
        
        time_spent = behavioral_data.get('timeSpent', 0)
        mouse_movements = behavioral_data.get('mouseMovements', 0)
        keyboard_events = behavioral_data.get('keyboardEvents', 0)
        scroll_behavior = behavioral_data.get('scrollBehavior', 0)
        
        # Zero interaction patterns
        if time_spent > 5000:  # More than 5 seconds
            total_interactions = mouse_movements + keyboard_events + scroll_behavior
            
            if total_interactions == 0:
                methods.append('zero_interaction')
                confidence += 0.7
            elif total_interactions < 3:
                methods.append('minimal_interaction')
                confidence += 0.4
        
        # Impossibly fast mouse movements
        mouse_velocity = behavioral_data.get('mouseVelocity', [])
        if mouse_velocity:
            avg_velocity = sum(mouse_velocity) / len(mouse_velocity)
            if avg_velocity > 3000:  # Impossibly fast
                methods.append('impossible_mouse_speed')
                confidence += 0.8
        
        # Perfect timing patterns
        click_timing = behavioral_data.get('clickTiming', [])
        if len(click_timing) > 3:
            intervals = [click_timing[i] - click_timing[i-1] for i in range(1, len(click_timing))]
            if intervals and all(abs(interval - intervals[0]) < 50 for interval in intervals):
                methods.append('perfect_timing')
                confidence += 0.6
        
        return {
            'suspicious': confidence >= 0.4,
            'confidence': confidence,
            'methods': methods
        }
    
    def _analyze_request_patterns(self, ip_address: str) -> Dict:
        """Analyze request patterns"""
        analysis = RequestPattern.analyze_patterns(ip_address, minutes=5)
        
        if analysis['request_count'] > 30:  # Lowered threshold
            return {
                'suspicious': True,
                'confidence': min(0.6 + (analysis['request_count'] - 30) * 0.01, 0.9),
                'methods': ['high_request_rate']
            }
        
        return {'suspicious': False, 'confidence': 0, 'methods': []}
    
    def _calculate_weighted_confidence(self, scores: List[float], layers: Dict) -> float:
        """Calculate weighted confidence score"""
        if not scores:
            return 0.0
        
        # Weight different detection methods
        weights = {
            'automation': 1.0,      # Automation tools = definitely bots
            'social_bot': 0.8,      # Social bots = legitimate but still bots
            'generic_bot': 0.7,     # Generic patterns = likely bots
            'ip_analysis': 0.4,     # IP reputation = supporting evidence
            'behavioral': 0.6,      # Behavior = good indicator
            'patterns': 0.5,        # Request patterns = supporting evidence
        }
        
        weighted_sum = 0
        total_weight = 0
        
        for layer_name, layer_data in layers.items():
            if layer_data.get('confidence', 0) > 0:
                weight = weights.get(layer_name, 0.5)
                weighted_sum += layer_data['confidence'] * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        final_score = weighted_sum / total_weight
        
        # Apply browser penalty
        if layers.get('browser_analysis', {}).get('is_browser', False):
            browser_confidence = layers['browser_analysis']['browser_confidence']
            penalty = browser_confidence * 0.7  # Strong browser indicators reduce bot confidence
            final_score = max(0, final_score - penalty)
        
        return min(final_score, 1.0)
    
    def _determine_bot_status(self, confidence: float, layers: Dict, is_facebook_bot: bool) -> bool:
        """Determine if request is from a bot"""
        # Facebook bots are always bots (but legitimate)
        if is_facebook_bot:
            return True
        
        # High confidence automation tools
        if layers.get('automation', {}).get('confidence', 0) >= 0.95:
            return True
        
        # Multiple weak signals can indicate bot
        detection_count = sum(1 for layer in layers.values() if layer.get('confidence', 0) > 0.3)
        
        if detection_count >= 3 and confidence >= 0.5:
            return True
        
        # Standard threshold
        return confidence >= 0.6
    
    def _calculate_risk_level(self, confidence: float, is_facebook_bot: bool) -> str:
        """Calculate risk level"""
        if is_facebook_bot:
            return 'low'  # Facebook bots are legitimate
        elif confidence >= 0.9:
            return 'critical'
        elif confidence >= 0.7:
            return 'high'
        elif confidence >= 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _recommend_action(self, confidence: float, is_bot: bool, is_facebook_bot: bool) -> str:
        """Recommend action based on detection"""
        if is_facebook_bot:
            return 'allow_with_seo_content'
        elif is_bot and confidence >= 0.8:
            return 'block'
        elif is_bot and confidence >= 0.6:
            return 'challenge'
        else:
            return 'allow'
    
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
    
    def _log_detection(self, request_data: Dict, result: Dict):
        """Log detection result"""
        try:
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
            
            print(f"📝 Logged detection: {detection.id}")
        except Exception as e:
            print(f"❌ Failed to log detection: {e}")
    
    def _execute_auto_response(self, ip_address: str, result: Dict):
        """Execute automatic response for detected bots"""
        try:
            if result['confidence'] >= 0.8 and not result.get('is_facebook_bot', False):
                print(f"🚫 Auto-blocking high confidence bot: {ip_address}")
                
                IPBlacklist.objects.get_or_create(
                    ip_address=ip_address,
                    defaults={
                        'reason': 'High confidence bot detection',
                        'confidence_score': result['confidence'],
                        'detection_method': 'auto_enhanced',
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
        """Load ML model (placeholder)"""
        return None
    
    def _load_scaler(self):
        """Load scaler (placeholder)"""
        return None
    
    def _load_ensemble_models(self):
        """Load ensemble models (placeholder)"""
        return {}
    
    def get_statistics(self) -> Dict:
        """Get detection statistics"""
        now = timezone.now()
        last_hour = now - timedelta(hours=1)
        last_24h = now - timedelta(hours=24)
        
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
        
        overall_stats = {
            'total_detections': BotDetection.objects.count(),
            'total_bots_detected': BotDetection.objects.filter(is_bot=True).count(),
            'total_humans_detected': BotDetection.objects.filter(is_bot=False).count(),
            'active_blacklist_entries': IPBlacklist.objects.filter(is_active=True).count(),
        }
        
        return {
            'last_hour': stats_1h,
            'last_24_hours': stats_24h,
            'overall': overall_stats,
            'system_health': {
                'mode': 'enhanced_detection',
                'detection_active': True,
                'thresholds_configured': True,
            },
            'generated_at': now.isoformat()
        }