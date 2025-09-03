# Enhanced Bot Detection Service - Ultra Advanced
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
    """Ultra-advanced bot detection service with multiple AI layers"""
    
    def __init__(self):
        # Advanced bot patterns with confidence scoring
        self.bot_patterns = [
            # Social media bots (highest priority)
            {'pattern': re.compile(r'facebook|facebookexternalhit|facebot|facebookcatalog', re.I), 'weight': 0.98, 'category': 'social'},
            {'pattern': re.compile(r'twitter|twitterbot|tweetmeme', re.I), 'weight': 0.95, 'category': 'social'},
            {'pattern': re.compile(r'linkedin|linkedinbot', re.I), 'weight': 0.95, 'category': 'social'},
            {'pattern': re.compile(r'instagram|instagrambot', re.I), 'weight': 0.95, 'category': 'social'},
            
            # Search engines and crawlers
            {'pattern': re.compile(r'google|googlebot|googleother|adsbot-google', re.I), 'weight': 0.92, 'category': 'search'},
            {'pattern': re.compile(r'bing|bingbot|msnbot|bingpreview', re.I), 'weight': 0.90, 'category': 'search'},
            {'pattern': re.compile(r'yahoo|slurp|yahooseeker', re.I), 'weight': 0.90, 'category': 'search'},
            {'pattern': re.compile(r'baidu|baiduspider|baiduimagebot', re.I), 'weight': 0.90, 'category': 'search'},
            {'pattern': re.compile(r'yandex|yandexbot|yandexmobilebot', re.I), 'weight': 0.90, 'category': 'search'},
            {'pattern': re.compile(r'duckduckgo|duckduckbot', re.I), 'weight': 0.88, 'category': 'search'},
            
            # Automation and testing tools (very high confidence)
            {'pattern': re.compile(r'selenium|webdriver', re.I), 'weight': 0.99, 'category': 'automation'},
            {'pattern': re.compile(r'puppeteer|playwright|chromium', re.I), 'weight': 0.98, 'category': 'automation'},
            {'pattern': re.compile(r'phantomjs|phantom|slimerjs', re.I), 'weight': 0.97, 'category': 'automation'},
            {'pattern': re.compile(r'headless|chrome-headless', re.I), 'weight': 0.96, 'category': 'automation'},
            
            # Script tools and libraries
            {'pattern': re.compile(r'curl|wget|httpie', re.I), 'weight': 0.95, 'category': 'script'},
            {'pattern': re.compile(r'python-requests|python-urllib|python-httpx', re.I), 'weight': 0.94, 'category': 'script'},
            {'pattern': re.compile(r'nodejs|node\.js|axios|fetch', re.I), 'weight': 0.92, 'category': 'script'},
            {'pattern': re.compile(r'ruby|mechanize|httparty', re.I), 'weight': 0.93, 'category': 'script'},
            {'pattern': re.compile(r'java|apache-httpclient|okhttp', re.I), 'weight': 0.91, 'category': 'script'},
            {'pattern': re.compile(r'go-http-client|golang', re.I), 'weight': 0.90, 'category': 'script'},
            
            # Generic bot indicators
            {'pattern': re.compile(r'\bbot\b|crawler|spider|scraper|scrape', re.I), 'weight': 0.85, 'category': 'generic'},
            {'pattern': re.compile(r'monitor|check|test|scan|probe', re.I), 'weight': 0.80, 'category': 'monitoring'},
            {'pattern': re.compile(r'feed|rss|sitemap|link.?check', re.I), 'weight': 0.75, 'category': 'utility'},
            
            # Advanced evasion attempts
            {'pattern': re.compile(r'mozilla/[45]\.0.*rv:[0-9]+.*firefox/[0-9]+.*', re.I), 'weight': 0.60, 'category': 'suspicious'},
            {'pattern': re.compile(r'chrome/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+.*safari/[0-9]+\.[0-9]+', re.I), 'weight': 0.55, 'category': 'suspicious'},
        ]
        
        # Advanced behavioral analysis thresholds
        self.behavior_thresholds = {
            'mouse_movement_entropy': 2.5,
            'click_timing_variance': 1000,
            'scroll_pattern_regularity': 0.8,
            'keyboard_rhythm_consistency': 0.9,
            'interaction_density': 0.1,  # interactions per second
            'velocity_outliers': 3.0,     # standard deviations
        }
        
        # Browser feature fingerprinting
        self.browser_features = {
            'webgl_required': True,
            'canvas_required': True,
            'audio_context_required': True,
            'device_memory_expected': True,
            'hardware_concurrency_expected': True,
            'touch_support_mobile_only': True,
        }
        
        # Network timing analysis
        self.timing_analysis = {
            'request_intervals': [],
            'response_times': [],
            'connection_patterns': {},
        }
        
        # Load ML models and scalers
        self.ml_model = self._load_ml_model()
        self.scaler = self._load_scaler()
        self.ensemble_models = self._load_ensemble_models()
        
        # Initialize GeoIP
        self.geoip_reader = self._initialize_geoip()
    
    def retrain_model(self, use_recent_data: bool = True, days_back: int = 30) -> Dict:
        """
        Retrain ML models using recent detection data
        
        Args:
            use_recent_data: Whether to use recent detection data for training
            days_back: How many days back to look for training data
        
        Returns:
            Dict containing training results and success status
        """
        try:
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import classification_report, accuracy_score
            
            # Collect training data
            training_data = []
            labels = []
            processed_count = 0  # Initialize the counter
            
            if use_recent_data and days_back > 0:
                # Get recent detection data
                cutoff_date = timezone.now() - timedelta(days=days_back)
                recent_detections = BotDetection.objects.filter(
                    timestamp__gte=cutoff_date,
                    confidence_score__gte=0.7  # Only high-confidence detections
                ).order_by('-timestamp')[:1000]  # Limit to prevent memory issues
                
                for detection in recent_detections:
                    # Reconstruct request data for feature extraction
                    request_data = {
                        'ip_address': detection.ip_address,
                        'user_agent': detection.user_agent,
                        'headers': detection.get_headers(),
                        'behavioral_data': detection.get_behavioral_data(),
                        'fingerprint': detection.fingerprint
                    }
                    
                    # Extract features using existing method
                    features = self._extract_advanced_features(request_data, {})
                    training_data.append(features)
                    labels.append(1 if detection.is_bot else 0)
                    processed_count += 1  # Increment the counter
            
            # If not enough real data, supplement with synthetic data
            if len(training_data) < 50:
                synthetic_normal = self._generate_synthetic_training_data()
                synthetic_bot = self._generate_synthetic_bot_data()
                
                training_data.extend(synthetic_normal)
                labels.extend([0] * len(synthetic_normal))
                
                training_data.extend(synthetic_bot)
                labels.extend([1] * len(synthetic_bot))
            
            if len(training_data) < 10:
                return {
                    'success': False,
                    'error': 'Insufficient training data',
                    'samples': len(training_data)
                }
            
            # Prepare data
            X = np.array(training_data)
            y = np.array(labels)
            
            # Scale features
            if self.scaler:
                X_scaled = self.scaler.fit_transform(X)
            else:
                self.scaler = StandardScaler()
                X_scaled = self.scaler.fit_transform(X)
            
            # Split data for validation
            if len(X) > 20:
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled, y, test_size=0.2, random_state=42, stratify=y
                )
            else:
                X_train, X_test, y_train, y_test = X_scaled, X_scaled, y, y
            
            # Retrain models
            results = {}
            
            # 1. Retrain Isolation Forest
            try:
                iso_forest = IsolationForest(
                    contamination=0.1,
                    random_state=42,
                    n_estimators=100
                )
                iso_forest.fit(X_train)
                
                # Test performance
                iso_pred = iso_forest.predict(X_test)
                iso_pred_binary = [0 if p == 1 else 1 for p in iso_pred]  # Convert to binary
                
                results['isolation_forest'] = {
                    'accuracy': accuracy_score(y_test, iso_pred_binary),
                    'trained': True
                }
                
                self.ensemble_models['isolation_forest'] = iso_forest
                
            except Exception as e:
                results['isolation_forest'] = {'error': str(e), 'trained': False}
            
            # 2. Retrain Random Forest (if we have labels)
            if len(set(y)) > 1:  # We have both classes
                try:
                    from sklearn.ensemble import RandomForestClassifier
                    
                    rf_model = RandomForestClassifier(
                        n_estimators=50,
                        random_state=42,
                        max_depth=10
                    )
                    rf_model.fit(X_train, y_train)
                    
                    # Test performance
                    rf_pred = rf_model.predict(X_test)
                    
                    results['random_forest'] = {
                        'accuracy': accuracy_score(y_test, rf_pred),
                        'trained': True
                    }
                    
                    self.ensemble_models['random_forest'] = rf_model
                    
                except Exception as e:
                    results['random_forest'] = {'error': str(e), 'trained': False}
            
            # 3. Retrain SVM
            try:
                from sklearn.svm import OneClassSVM
                
                svm_model = OneClassSVM(gamma='scale', nu=0.1)
                svm_model.fit(X_train)
                
                # Test performance
                svm_pred = svm_model.predict(X_test)
                svm_pred_binary = [0 if p == 1 else 1 for p in svm_pred]
                
                results['svm'] = {
                    'accuracy': accuracy_score(y_test, svm_pred_binary),
                    'trained': True
                }
                
                self.ensemble_models['svm'] = svm_model
                
            except Exception as e:
                results['svm'] = {'error': str(e), 'trained': False}
            
            # Save models
            models_dir = os.path.join(settings.BASE_DIR, 'ml_models')
            os.makedirs(models_dir, exist_ok=True)
            
            saved_models = []
            for model_name, model in self.ensemble_models.items():
                try:
                    model_path = os.path.join(models_dir, f'bot_detector_{model_name}.joblib')
                    joblib.dump(model, model_path)
                    saved_models.append(model_name)
                except Exception as e:
                    results[f'{model_name}_save_error'] = str(e)
            
            # Save scaler
            try:
                scaler_path = os.path.join(models_dir, 'feature_scaler.joblib')
                joblib.dump(self.scaler, scaler_path)
                saved_models.append('scaler')
            except Exception as e:
                results['scaler_save_error'] = str(e)
            
            # Log retraining event
            SecurityLog.log_event(
                event_type='model_retrained',
                ip_address='system',
                description=f'ML models retrained with {len(training_data)} samples',
                severity='info',
                details={
                    'samples_used': len(training_data),
                    'models_trained': list(results.keys()),
                    'saved_models': saved_models,
                    'training_accuracy': {k: v.get('accuracy') for k, v in results.items() if 'accuracy' in v}
                }
            )
            
            return {
                'success': True,
                'models_trained': len([r for r in results.values() if r.get('trained', False)]),
                'total_samples': len(training_data),
                'real_samples': processed_count,  # Now properly defined
                'synthetic_samples': len(training_data) - processed_count,
                'results': results,
                'saved_models': saved_models
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'models_trained': 0
            }

    def _generate_synthetic_bot_data(self) -> List[List[float]]:
        """Generate synthetic bot training data"""
        bot_data = []
        
        # Generate various bot patterns
        for _ in range(30):
            features = [
                np.random.normal(40, 15),   # Shorter UA length
                np.random.normal(6, 2),     # Fewer UA words
                np.random.normal(6, 2),     # More slashes (API calls)
                np.random.normal(1, 0.5),   # Fewer parentheses
                np.random.choice([0, 1]),   # May not have Mozilla
                np.random.choice([0, 1]),   # May not have Chrome
                0, 0,  # Usually missing Safari/Firefox
                np.random.normal(4, 1),     # Fewer headers
                np.random.choice([0, 1]),   # Missing essential headers
                np.random.choice([0, 1]),
                np.random.choice([0, 1]),
                np.random.choice([0, 1]),
                0.9, 6,  # High detection confidence
                0.8, 5,
                0.7, 4,
                0.6, 3,
                0.5, 2,
                0,  # No mouse movements
                0,  # No entropy
                0,  # No keyboard events
                np.random.normal(1000, 300), # Very short time
                0,  # No clicks
                0,  # No scrolling
            ]
            
            # Pad to 50 features
            while len(features) < 50:
                features.append(np.random.normal(0, 0.1))
            
            bot_data.append(features[:50])
        
        return bot_data

    def detect_bot(self, request_data: Dict) -> Dict:
        """
        Ultra-advanced bot detection with multiple layers
        Returns comprehensive detection result
        """
        ip_address = request_data.get('ip_address')
        user_agent = request_data.get('user_agent', '')
        headers = request_data.get('headers', {})
        behavioral_data = request_data.get('behavioral_data', {})
        
        # Initialize detection layers
        detection_layers = {}
        confidence_scores = []
        all_methods = []
        
        # Layer 1: IP Reputation and Blacklist
        layer1 = self._analyze_ip_reputation(ip_address or "")
        if layer1['confidence'] > 0:
            detection_layers['ip_reputation'] = layer1
            confidence_scores.append(layer1['confidence'] * 0.25)
            all_methods.extend(layer1['methods'])
        
        # Layer 2: Advanced User Agent Analysis
        layer2 = self._analyze_user_agent_advanced(user_agent)
        if layer2['confidence'] > 0:
            detection_layers['user_agent'] = layer2
            confidence_scores.append(layer2['confidence'] * 0.20)
            all_methods.extend(layer2['methods'])
        
        # Layer 3: HTTP Headers Deep Analysis
        layer3 = self._analyze_headers_advanced(headers)
        if layer3['confidence'] > 0:
            detection_layers['headers'] = layer3
            confidence_scores.append(layer3['confidence'] * 0.15)
            all_methods.extend(layer3['methods'])
        
        # Layer 4: Behavioral Pattern Analysis
        if behavioral_data:
            layer4 = self._analyze_behavior_advanced(behavioral_data)
            if layer4['confidence'] > 0:
                detection_layers['behavioral'] = layer4
                confidence_scores.append(layer4['confidence'] * 0.25)
                all_methods.extend(layer4['methods'])
        
        # Layer 5: Request Pattern and Timing Analysis
        layer5 = self._analyze_request_patterns_advanced(ip_address or "", request_data)
        if layer5['confidence'] > 0:
            detection_layers['request_patterns'] = layer5
            confidence_scores.append(layer5['confidence'] * 0.10)
            all_methods.extend(layer5['methods'])
        
        # Layer 6: Browser Fingerprint Analysis
        layer6 = self._analyze_browser_fingerprint(request_data.get('fingerprint', ''), behavioral_data)
        if layer6['confidence'] > 0:
            detection_layers['fingerprint'] = layer6
            confidence_scores.append(layer6['confidence'] * 0.15)
            all_methods.extend(layer6['methods'])
        
        # Layer 7: Advanced ML Ensemble
        layer7 = self._ml_ensemble_predict(request_data, detection_layers)
        if layer7['confidence'] > 0:
            detection_layers['ml_ensemble'] = layer7
            confidence_scores.append(layer7['confidence'] * 0.30)
            all_methods.extend(layer7['methods'])
        
        # Calculate weighted confidence with layer importance
        final_confidence = self._calculate_advanced_confidence(confidence_scores, detection_layers)
        is_bot = final_confidence >= 0.6
        
        # Geographic and threat intelligence
        geo_info = self._get_advanced_geo_info(ip_address or "")
        threat_intel = self._check_threat_intelligence_advanced(ip_address or "", user_agent)
        
        # Compile comprehensive result
        result = {
            'is_bot': is_bot,
            'confidence': round(final_confidence, 4),
            'methods': list(set(all_methods)),
            'geo_info': geo_info,
            'threat_intel': threat_intel,
            'detection_layers': detection_layers,
            'analysis_timestamp': timezone.now().isoformat(),
            'risk_level': self._calculate_risk_level(final_confidence, detection_layers),
            'recommended_action': self._recommend_action(final_confidence, detection_layers)
        }
        
        # Advanced logging and response
        self._log_advanced_detection(request_data, result)
        
        # Auto-actions based on confidence and risk
        if is_bot and final_confidence >= 0.85:
            self._execute_auto_response(ip_address or "", result, request_data)
        
        return result
    
    def _analyze_user_agent_advanced(self, user_agent: str) -> Dict:
        """Advanced user agent analysis with multiple detection vectors"""
        if not user_agent:
            return {
                'confidence': 0.85,
                'methods': ['missing_user_agent'],
                'details': 'No user agent provided'
            }
        
        methods = []
        confidence = 0
        details = {}
        
        # Pattern matching with weighted scoring
        pattern_matches = []
        for bot_pattern in self.bot_patterns:
            if bot_pattern['pattern'].search(user_agent):
                pattern_matches.append(bot_pattern)
                confidence = max(confidence, bot_pattern['weight'])
                methods.append(f"pattern_{bot_pattern['category']}")
        
        details['pattern_matches'] = [p['category'] for p in pattern_matches]
        
        # Length analysis
        ua_length = len(user_agent)
        if ua_length < 20:
            methods.append('extremely_short_ua')
            confidence = max(confidence, 0.80)
        elif ua_length < 50:
            methods.append('short_ua')
            confidence = max(confidence, 0.60)
        elif ua_length > 1000:
            methods.append('extremely_long_ua')
            confidence = max(confidence, 0.70)
        
        # Browser version analysis
        chrome_match = re.search(r'Chrome/(\d+)\.(\d+)\.(\d+)\.(\d+)', user_agent)
        if chrome_match:
            version = int(chrome_match.group(1))
            if version < 70 or version > 150:  # Suspicious version range
                methods.append('suspicious_chrome_version')
                confidence = max(confidence, 0.50)
                details['chrome_version'] = version
        
        # OS consistency checks
        os_inconsistencies = self._check_os_consistency(user_agent)
        if os_inconsistencies:
            methods.extend(os_inconsistencies)
            confidence = max(confidence, 0.45)
        
        # Browser feature consistency
        feature_inconsistencies = self._check_browser_features(user_agent)
        if feature_inconsistencies:
            methods.extend(feature_inconsistencies)
            confidence = max(confidence, 0.40)
        
        # Entropy analysis of the user agent string
        ua_entropy = self._calculate_string_entropy(user_agent)
        if ua_entropy < 3.0:  # Very low entropy suggests synthetic UA
            methods.append('low_entropy_ua')
            confidence = max(confidence, 0.35)
            details['entropy'] = ua_entropy
        
        return {
            'confidence': confidence,
            'methods': methods,
            'details': details
        }
    
    def _analyze_behavior_advanced(self, behavioral_data: Dict) -> Dict:
        """Advanced behavioral analysis with multiple biometric vectors"""
        methods = []
        confidence = 0
        analysis = {}
        
        # Extract behavioral metrics
        mouse_movements = behavioral_data.get('mouseMovements', 0)
        mouse_entropy = behavioral_data.get('mouseEntropy', 0)
        click_patterns = behavioral_data.get('clickPatterns', [])
        scroll_behavior = behavioral_data.get('scrollBehavior', 0)
        keyboard_events = behavioral_data.get('keyboardEvents', 0)
        time_spent = behavioral_data.get('timeSpent', 0)
        mouse_velocity = behavioral_data.get('mouseVelocity', [])
        click_timing = behavioral_data.get('clickTiming', [])
        
        # Zero interaction analysis
        if time_spent > 5000:
            if mouse_movements == 0:
                methods.append('no_mouse_movement')
                confidence += 0.40
            
            if keyboard_events == 0:
                methods.append('no_keyboard_interaction')
                confidence += 0.25
            
            if scroll_behavior == 0:
                methods.append('no_scrolling')
                confidence += 0.20
        
        # Mouse movement entropy analysis
        if mouse_movements > 50:
            if mouse_entropy < self.behavior_thresholds['mouse_movement_entropy']:
                methods.append('low_mouse_entropy')
                confidence += 0.35
                analysis['mouse_entropy'] = mouse_entropy
        
        # Click pattern analysis
        if len(click_patterns) > 3:
            click_stats = self._analyze_click_patterns(click_patterns)
            if click_stats['too_regular']:
                methods.append('robotic_clicking')
                confidence += 0.45
            if click_stats['too_fast']:
                methods.append('impossible_click_speed')
                confidence += 0.60
            analysis['click_analysis'] = click_stats
        
        # Mouse velocity analysis
        if len(mouse_velocity) > 10:
            velocity_analysis = self._analyze_mouse_velocity(mouse_velocity)
            if velocity_analysis['suspicious']:
                methods.append('suspicious_mouse_velocity')
                confidence += 0.30
                analysis['velocity_analysis'] = velocity_analysis
        
        # Interaction density analysis
        if time_spent > 1000:
            total_interactions = mouse_movements + keyboard_events + scroll_behavior
            interaction_rate = total_interactions / (time_spent / 1000)
            
            if interaction_rate == 0:
                methods.append('zero_interaction_rate')
                confidence += 0.50
            elif interaction_rate > 50:  # Impossibly high interaction rate
                methods.append('superhuman_interaction_rate')
                confidence += 0.40
            
            analysis['interaction_rate'] = interaction_rate
        
        # Device motion and orientation analysis
        has_device_motion = behavioral_data.get('deviceMotion', False)
        has_orientation = behavioral_data.get('orientationChange', False)
        
        if not has_device_motion and not has_orientation and time_spent > 10000:
            # Lack of natural device movement over time
            methods.append('no_device_physics')
            confidence += 0.25
        
        # Browser feature analysis
        webgl_support = behavioral_data.get('webglSupport', False)
        if not webgl_support:
            methods.append('no_webgl_support')
            confidence += 0.30
        
        # Screen and viewport analysis
        screen_resolution = behavioral_data.get('screenResolution', '')
        if screen_resolution:
            screen_analysis = self._analyze_screen_metrics(screen_resolution)
            if screen_analysis['suspicious']:
                methods.append('suspicious_screen_metrics')
                confidence += 0.20
                analysis['screen_analysis'] = screen_analysis
        
        return {
            'confidence': min(confidence, 1.0),
            'methods': methods,
            'analysis': analysis
        }
    
    def _analyze_headers_advanced(self, headers: Dict) -> Dict:
        """Advanced HTTP header analysis"""
        methods = []
        confidence = 0
        analysis = {}
        
        # Convert to lowercase for analysis
        headers_lower = {k.lower(): v for k, v in headers.items()}
        
        # Essential header checks
        missing_headers = []
        suspicious_headers = []
        
        expected_headers = ['accept', 'accept-language', 'accept-encoding', 'user-agent']
        for header in expected_headers:
            if header not in headers_lower:
                missing_headers.append(header)
                confidence += 0.15
        
        if missing_headers:
            methods.append('missing_essential_headers')
            analysis['missing_headers'] = missing_headers
        
        # Accept header analysis
        if 'accept' in headers_lower:
            accept_value = headers_lower['accept']
            if not accept_value.startswith('text/html'):
                methods.append('non_browser_accept')
                confidence += 0.35
            if '*/*' == accept_value.strip():
                methods.append('generic_accept_header')
                confidence += 0.25
        
        # Accept-Language analysis
        if 'accept-language' in headers_lower:
            lang_header = headers_lower['accept-language']
            if not re.search(r'[a-z]{2}(-[A-Z]{2})?', lang_header):
                methods.append('malformed_accept_language')
                confidence += 0.30
        
        # Connection header analysis
        if 'connection' in headers_lower:
            conn_value = headers_lower['connection'].lower()
            if conn_value not in ['keep-alive', 'close']:
                methods.append('unusual_connection_header')
                confidence += 0.20
        
        # Bot-specific headers
        bot_headers = [
            'x-forwarded-for', 'x-real-ip', 'x-cluster-client-ip',
            'x-forwarded-proto', 'x-requested-with', 'x-forwarded-host'
        ]
        
        found_bot_headers = [h for h in bot_headers if h in headers_lower]
        if len(found_bot_headers) > 2:
            methods.append('multiple_proxy_headers')
            confidence += 0.25
            analysis['bot_headers'] = found_bot_headers
        
        # Header order analysis (browsers have typical patterns)
        header_order_score = self._analyze_header_order(list(headers.keys()))
        if header_order_score < 0.5:
            methods.append('unusual_header_order')
            confidence += 0.15
            analysis['order_score'] = header_order_score
        
        # DNT (Do Not Track) analysis
        if 'dnt' in headers_lower:
            # Bots often don't set this header correctly
            dnt_value = headers_lower['dnt']
            if dnt_value not in ['0', '1']:
                methods.append('invalid_dnt_header')
                confidence += 0.10
        
        return {
            'confidence': min(confidence, 1.0),
            'methods': methods,
            'analysis': analysis
        }
    
    def _analyze_browser_fingerprint(self, fingerprint: str, behavioral_data: Dict) -> Dict:
        """Analyze browser fingerprint for bot indicators"""
        methods = []
        confidence = 0
        analysis = {}
        
        if not fingerprint:
            methods.append('missing_fingerprint')
            return {'confidence': 0.30, 'methods': methods, 'analysis': analysis}
        
        try:
            # Decode fingerprint components
            decoded = self._decode_fingerprint(fingerprint)
            
            # Screen resolution analysis
            if 'screen' in decoded:
                screen_analysis = self._analyze_screen_fingerprint(decoded['screen'])
                if screen_analysis['suspicious']:
                    methods.append('suspicious_screen_fingerprint')
                    confidence += 0.25
                    analysis['screen'] = screen_analysis
            
            # WebGL analysis
            if 'webgl' in decoded:
                webgl_analysis = self._analyze_webgl_fingerprint(decoded['webgl'])
                if webgl_analysis['suspicious']:
                    methods.append('suspicious_webgl_fingerprint')
                    confidence += 0.30
                    analysis['webgl'] = webgl_analysis
            
            # Canvas fingerprint analysis
            if 'canvas' in decoded:
                canvas_analysis = self._analyze_canvas_fingerprint(decoded['canvas'])
                if canvas_analysis['suspicious']:
                    methods.append('suspicious_canvas_fingerprint')
                    confidence += 0.35
                    analysis['canvas'] = canvas_analysis
            
            # Audio fingerprint analysis
            if 'audio' in decoded:
                audio_analysis = self._analyze_audio_fingerprint(decoded['audio'])
                if audio_analysis['suspicious']:
                    methods.append('suspicious_audio_fingerprint')
                    confidence += 0.25
                    analysis['audio'] = audio_analysis
            
            # Font analysis
            if 'fonts' in decoded:
                font_count = int(decoded['fonts'].split(':')[1]) if ':' in decoded['fonts'] else 0
                if font_count == 0:
                    methods.append('no_fonts_detected')
                    confidence += 0.40
                elif font_count > 200:
                    methods.append('excessive_fonts')
                    confidence += 0.20
                analysis['font_count'] = font_count
            
            # Plugin analysis
            if 'plugins' in decoded:
                plugin_analysis = self._analyze_plugin_fingerprint(decoded['plugins'])
                if plugin_analysis['suspicious']:
                    methods.append('suspicious_plugins')
                    confidence += 0.30
                    analysis['plugins'] = plugin_analysis
            
        except Exception as e:
            methods.append('fingerprint_decode_error')
            confidence += 0.20
            analysis['error'] = str(e)
        
        return {
            'confidence': min(confidence, 1.0),
            'methods': methods,
            'analysis': analysis
        }
    
    def _ml_ensemble_predict(self, request_data: Dict, detection_layers: Dict) -> Dict:
        """Advanced ML ensemble prediction with multiple models"""
        if not self.ensemble_models:
            return {'confidence': 0, 'methods': [], 'details': 'ML models not available'}
        
        try:
            # Extract comprehensive features
            features = self._extract_advanced_features(request_data, detection_layers)
            
            # Get predictions from multiple models
            predictions = {}
            confidence_scores = []
            
            for model_name, model in self.ensemble_models.items():
                try:
                    if hasattr(model, 'predict_proba'):
                        # Classification model
                        prob = model.predict_proba([features])[0]
                        bot_probability = prob[1] if len(prob) > 1 else prob[0]
                        predictions[model_name] = bot_probability
                        confidence_scores.append(bot_probability)
                    else:
                        # Anomaly detection model
                        anomaly_score = model.decision_function([features])[0]
                        is_anomaly = model.predict([features])[0] == -1
                        if is_anomaly:
                            bot_probability = min(1.0, max(0.0, (-anomaly_score + 0.5) / 2))
                            predictions[model_name] = bot_probability
                            confidence_scores.append(bot_probability)
                        else:
                            predictions[model_name] = 0.0
                            confidence_scores.append(0.0)
                            
                except Exception as e:
                    predictions[model_name] = f"Error: {str(e)}"
            
            # Ensemble prediction with weighted voting
            if confidence_scores:
                ensemble_confidence = self._calculate_ensemble_confidence(confidence_scores, predictions)
                methods = ['ml_ensemble']
                
                # Add specific model indicators
                for model_name, score in predictions.items():
                    if isinstance(score, (int, float)) and score > 0.7:
                        methods.append(f'ml_{model_name}_positive')
            else:
                ensemble_confidence = 0.0
                methods = []
            
            return {
                'confidence': ensemble_confidence,
                'methods': methods,
                'details': {
                    'individual_predictions': predictions,
                    'feature_count': len(features),
                    'ensemble_method': 'weighted_voting'
                }
            }
            
        except Exception as e:
            return {
                'confidence': 0,
                'methods': ['ml_ensemble_error'],
                'details': f'ML prediction error: {str(e)}'
            }
    
    # Helper methods for advanced analysis
    
    def _analyze_click_patterns(self, click_patterns: List[int]) -> Dict:
        """Analyze click timing patterns for bot indicators"""
        if len(click_patterns) < 3:
            return {'too_regular': False, 'too_fast': False}
        
        avg_interval = statistics.mean(click_patterns)
        std_dev = statistics.stdev(click_patterns) if len(click_patterns) > 1 else 0
        
        # Check for impossibly fast clicking
        too_fast = avg_interval < 50  # Less than 50ms average
        
        # Check for robotic regularity
        coefficient_of_variation = (std_dev / avg_interval) if avg_interval > 0 else 0
        too_regular = coefficient_of_variation < 0.1  # Very low variation
        
        return {
            'too_regular': too_regular,
            'too_fast': too_fast,
            'avg_interval': avg_interval,
            'std_dev': std_dev,
            'coefficient_of_variation': coefficient_of_variation
        }
    
    def _analyze_mouse_velocity(self, velocities: List[float]) -> Dict:
        """Analyze mouse velocity patterns"""
        if len(velocities) < 10:
            return {'suspicious': False}
        
        avg_velocity = statistics.mean(velocities)
        std_dev = statistics.stdev(velocities)
        
        # Check for suspicious patterns
        suspicious = False
        reasons = []
        
        if avg_velocity > 2000:  # Impossibly fast
            suspicious = True
            reasons.append('impossibly_fast')
        elif avg_velocity < 1 and avg_velocity > 0:  # Impossibly slow but moving
            suspicious = True
            reasons.append('impossibly_slow')
        
        # Check for too consistent velocity
        if std_dev < 10 and avg_velocity > 10:
            suspicious = True
            reasons.append('too_consistent')
        
        return {
            'suspicious': suspicious,
            'reasons': reasons,
            'avg_velocity': avg_velocity,
            'std_dev': std_dev
        }
    
    def _calculate_string_entropy(self, s: str) -> float:
        """Calculate Shannon entropy of a string"""
        if not s:
            return 0.0
        
        # Count character frequencies
        char_counts = {}
        for char in s:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        length = len(s)
        entropy = 0.0
        
        for count in char_counts.values():
            if count > 0:
                probability = count / length
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _calculate_advanced_confidence(self, scores: List[float], layers: Dict) -> float:
        """Calculate final confidence using advanced weighting"""
        if not scores:
            return 0.0
        
        # Layer weights based on reliability
        layer_weights = {
            'ip_reputation': 1.2,
            'user_agent': 1.0,
            'headers': 0.8,
            'behavioral': 1.1,
            'request_patterns': 0.9,
            'fingerprint': 1.0,
            'ml_ensemble': 1.3
        }
        
        # Calculate weighted score
        weighted_scores = []
        for layer_name, layer_data in layers.items():
            weight = layer_weights.get(layer_name, 1.0)
            confidence = layer_data.get('confidence', 0)
            
            # Boost confidence for multiple detection methods in same layer
            method_count = len(layer_data.get('methods', []))
            method_boost = min(0.1 * (method_count - 1), 0.3)
            
            weighted_score = (confidence + method_boost) * weight
            weighted_scores.append(weighted_score)
        
        # Use maximum weighted score with slight ensemble boost
        if weighted_scores:
            max_score = max(weighted_scores)
            ensemble_boost = 0.05 * (len(weighted_scores) - 1)  # Small boost for multiple layers
            final_score = min(max_score + ensemble_boost, 1.0)
        else:
            final_score = 0.0
        
        return final_score
    
    def _load_ensemble_models(self) -> Dict:
        """Load multiple ML models for ensemble prediction"""
        models = {}
        models_dir = os.path.join(settings.BASE_DIR, 'ml_models')
        
        try:
            # Load different model types
            model_files = {
                'isolation_forest': 'bot_detector_isolation.joblib',
                'random_forest': 'bot_detector_rf.joblib',
                'svm': 'bot_detector_svm.joblib',
                'neural_network': 'bot_detector_nn.joblib'
            }
            
            for model_name, filename in model_files.items():
                model_path = os.path.join(models_dir, filename)
                if os.path.exists(model_path):
                    models[model_name] = joblib.load(model_path)
                    print(f"Loaded {model_name} model")
            
            if not models:
                # Create and train basic ensemble if no models exist
                models = self._create_basic_ensemble()
                
        except Exception as e:
            print(f"Failed to load ensemble models: {e}")
            
        return models
    
    def _extract_advanced_features(self, request_data: Dict, layers: Dict) -> List[float]:
        """Extract comprehensive feature set for ML models"""
        features = []
        
        # Basic features
        user_agent = request_data.get('user_agent', '')
        features.extend([
            len(user_agent),
            len(user_agent.split()),
            user_agent.count('/'),
            user_agent.count('('),
            user_agent.count(')'),
            1 if 'Mozilla' in user_agent else 0,
            1 if 'Chrome' in user_agent else 0,
            1 if 'Safari' in user_agent else 0,
            1 if 'Firefox' in user_agent else 0,
        ])
        
        # Layer confidence scores
        for layer_name in ['ip_reputation', 'user_agent', 'headers', 'behavioral', 'fingerprint']:
            layer_data = layers.get(layer_name, {})
            features.append(layer_data.get('confidence', 0))
            features.append(len(layer_data.get('methods', [])))
        
        # Behavioral features
        behavioral = request_data.get('behavioral_data', {})
        features.extend([
            behavioral.get('mouseMovements', 0) / 1000.0,  # Normalize
            behavioral.get('mouseEntropy', 0),
            behavioral.get('keyboardEvents', 0) / 100.0,
            behavioral.get('timeSpent', 0) / 10000.0,
            len(behavioral.get('clickPatterns', [])),
            behavioral.get('scrollBehavior', 0) / 100.0,
        ])
        
        # Header features
        headers = request_data.get('headers', {})
        features.extend([
            len(headers),
            1 if 'accept' in headers else 0,
            1 if 'accept-language' in headers else 0,
            1 if 'accept-encoding' in headers else 0,
        ])
        
        # Pad to consistent length
        target_length = 50
        while len(features) < target_length:
            features.append(0.0)
        
        return features[:target_length]
    
    def _initialize_geoip(self):
        """Initialize GeoIP database"""
        try:
            geoip_path = getattr(settings, 'GEOIP_PATH', None)
            if geoip_path and os.path.exists(os.path.join(geoip_path, 'GeoLite2-City.mmdb')):
                return geoip2.database.Reader(os.path.join(geoip_path, 'GeoLite2-City.mmdb'))
        except Exception as e:
            print(f"Failed to initialize GeoIP: {e}")
        return None
    def _analyze_ip_reputation(self, ip_address: str) -> Dict:
        """Analyze IP reputation and blacklist status"""
        if not ip_address:
            return {'confidence': 0, 'methods': [], 'details': 'No IP provided'}
        
        methods = []
        confidence = 0
        
        # Check blacklist
        if IPBlacklist.is_blacklisted(ip_address):
            methods.append('ip_blacklisted')
            confidence = 0.95
        
        # Check for common bot IP ranges
        if self._is_datacenter_ip(ip_address):
            methods.append('datacenter_ip')
            confidence = max(confidence, 0.40)
        
        return {'confidence': confidence, 'methods': methods}
    
    def _is_datacenter_ip(self, ip_address: str) -> bool:
        """Check if IP is from a known datacenter range"""
        # Common cloud/hosting providers (simplified)
        datacenter_ranges = [
            '52.', '54.', '3.', '13.', '15.',  # AWS
            '35.', '34.', '104.',              # Google Cloud
            '40.', '52.', '13.', '20.',        # Azure
            '167.', '138.', '159.'             # DigitalOcean
        ]
        
        return any(ip_address.startswith(prefix) for prefix in datacenter_ranges)
    
    def _analyze_request_patterns_advanced(self, ip_address: str, request_data: Dict) -> Dict:
        """Advanced request pattern analysis"""
        methods = []
        confidence = 0
        
        # Use existing RequestPattern analysis
        analysis = RequestPattern.analyze_patterns(ip_address, minutes=10)
        
        if analysis['suspicious']:
            methods.extend(analysis['reasons'])
            confidence = 0.6 if analysis['request_count'] > 50 else 0.4
        
        return {'confidence': confidence, 'methods': methods, 'details': analysis}
    
    def _check_threat_intelligence_advanced(self, ip_address: str, user_agent: str) -> Dict:
        """Advanced threat intelligence checking"""
        cache_key = f"threat_intel_adv_{ip_address}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        methods = []
        confidence = 0
        
        # Check database threats
        threats = ThreatIntelligence.objects.filter(
            ip_address=ip_address,
            is_active=True
        )
        
        for threat in threats:
            methods.append(f'threat_{threat.threat_type}')
            confidence = max(confidence, threat.confidence)
        
        result = {'confidence': confidence, 'methods': methods}
        cache.set(cache_key, result, 1800)  # 30 minutes
        return result
    
    def _get_advanced_geo_info(self, ip_address: str) -> Dict:
        """Get advanced geographic information"""
        if not self.geoip_reader:
            return {}
        
        try:
            response = self.geoip_reader.city(ip_address)
            return {
                'country': response.country.iso_code,
                'country_name': response.country.name,
                'city': response.city.name,
                'latitude': float(response.location.latitude) if response.location.latitude else None,
                'longitude': float(response.location.longitude) if response.location.longitude else None,
                'is_eu': response.country.is_in_european_union,
                'accuracy_radius': response.location.accuracy_radius,
                'time_zone': response.location.time_zone
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _decode_fingerprint(self, fingerprint: str) -> Dict:
        """Decode base64 fingerprint into components"""
        try:
            decoded = base64.b64decode(fingerprint).decode('utf-8')
            components = {}
            
            for component in decoded.split('|'):
                if ':' in component:
                    key, value = component.split(':', 1)
                    components[key] = value
            
            return components
        except Exception:
            return {}
    
    def _analyze_screen_fingerprint(self, screen_data: str) -> Dict:
        """Analyze screen fingerprint for suspicious patterns"""
        if not screen_data:
            return {'suspicious': False}
        
        # Parse screen dimensions
        try:
            parts = screen_data.split('x')
            width = int(parts[0])
            height = int(parts[1])
            depth = int(parts[2]) if len(parts) > 2 else 24
            
            # Suspicious patterns
            if width == height:  # Square screens are uncommon
                return {'suspicious': True, 'reason': 'square_screen'}
            
            if width < 800 or height < 600:  # Very small screens
                return {'suspicious': True, 'reason': 'tiny_screen'}
            
            if width > 8000 or height > 8000:  # Impossibly large
                return {'suspicious': True, 'reason': 'impossible_size'}
            
            if depth not in [16, 24, 32]:  # Unusual color depth
                return {'suspicious': True, 'reason': 'unusual_depth'}
                
        except (ValueError, IndexError):
            return {'suspicious': True, 'reason': 'malformed_screen_data'}
        
        return {'suspicious': False}
    
    def _analyze_webgl_fingerprint(self, webgl_data: str) -> Dict:
        """Analyze WebGL fingerprint"""
        if not webgl_data or webgl_data == 'unavailable':
            return {'suspicious': True, 'reason': 'no_webgl'}
        
        # Most modern browsers support WebGL
        return {'suspicious': False}
    
    def _analyze_canvas_fingerprint(self, canvas_data: str) -> Dict:
        """Analyze canvas fingerprint"""
        if not canvas_data:
            return {'suspicious': True, 'reason': 'no_canvas'}
        
        # Check for common bot canvas signatures
        if len(canvas_data) < 10:
            return {'suspicious': True, 'reason': 'short_canvas_hash'}
        
        return {'suspicious': False}
    
    def _analyze_audio_fingerprint(self, audio_data: str) -> Dict:
        """Analyze audio context fingerprint"""
        if not audio_data or audio_data == 'unavailable':
            return {'suspicious': True, 'reason': 'no_audio_context'}
        
        return {'suspicious': False}
    
    def _analyze_plugin_fingerprint(self, plugin_data: str) -> Dict:
        """Analyze browser plugins"""
        if not plugin_data:
            return {'suspicious': True, 'reason': 'no_plugins'}
        
        # Desktop browsers usually have some plugins
        if 'Mobile' not in plugin_data and plugin_data == '0':
            return {'suspicious': True, 'reason': 'desktop_no_plugins'}
        
        return {'suspicious': False}
    
    def _analyze_screen_metrics(self, screen_resolution: str) -> Dict:
        """Analyze screen metrics for bot indicators"""
        try:
            if 'x' not in screen_resolution:
                return {'suspicious': True, 'reason': 'malformed_resolution'}
            
            width, height = map(int, screen_resolution.split('x'))
            
            # Common bot screen sizes
            bot_resolutions = [
                (1920, 1080), (1366, 768), (1280, 1024),  # Too common/perfect
                (800, 600), (1024, 768)  # Old/fake resolutions
            ]
            
            if (width, height) in bot_resolutions:
                return {'suspicious': True, 'reason': 'common_bot_resolution'}
            
            return {'suspicious': False}
            
        except (ValueError, AttributeError):
            return {'suspicious': True, 'reason': 'invalid_resolution_format'}
    
    def _analyze_header_order(self, headers: List[str]) -> float:
        """Analyze HTTP header order patterns"""
        # Typical browser header order
        typical_order = [
            'host', 'connection', 'user-agent', 'accept', 
            'accept-language', 'accept-encoding', 'referer'
        ]
        
        if not headers:
            return 0.0
        
        # Convert to lowercase for comparison
        headers_lower = [h.lower() for h in headers]
        
        # Calculate order similarity score
        matches = 0
        for i, expected_header in enumerate(typical_order):
            if i < len(headers_lower) and headers_lower[i] == expected_header:
                matches += 1
        
        return matches / len(typical_order)
    
    def _check_os_consistency(self, user_agent: str) -> List[str]:
        """Check for OS version inconsistencies"""
        issues = []
        
        # Windows version checks
        if 'Windows NT' in user_agent:
            # Extract Windows version
            nt_match = re.search(r'Windows NT ([\d.]+)', user_agent)
            if nt_match:
                nt_version = nt_match.group(1)
                # Check for impossible versions
                if nt_version in ['1.0', '2.0', '3.0']:
                    issues.append('impossible_windows_version')
                elif float(nt_version.split('.')[0]) > 15:  # Future versions
                    issues.append('future_windows_version')
        
        # macOS version checks
        if 'Mac OS X' in user_agent:
            mac_match = re.search(r'Mac OS X ([\d_]+)', user_agent)
            if mac_match:
                mac_version = mac_match.group(1).replace('_', '.')
                try:
                    major_version = int(mac_version.split('.')[0])
                    if major_version > 15 or major_version < 10:  # Reasonable range
                        issues.append('suspicious_macos_version')
                except ValueError:
                    issues.append('malformed_macos_version')
        
        return issues
    
    def _check_browser_features(self, user_agent: str) -> List[str]:
        """Check browser feature consistency"""
        issues = []
        
        # Chrome-specific checks
        if 'Chrome' in user_agent:
            # Should have Safari in the string too
            if 'Safari' not in user_agent:
                issues.append('chrome_missing_safari')
            
            # Check for WebKit
            if 'WebKit' not in user_agent:
                issues.append('chrome_missing_webkit')
        
        # Firefox checks
        if 'Firefox' in user_agent:
            # Should have Gecko
            if 'Gecko' not in user_agent:
                issues.append('firefox_missing_gecko')
        
        # Safari checks
        if 'Safari' in user_agent and 'Version' not in user_agent:
            if 'Chrome' not in user_agent:  # Not Chrome masquerading
                issues.append('safari_missing_version')
        
        return issues
    
    def _calculate_ensemble_confidence(self, scores: List[float], predictions: Dict) -> float:
        """Calculate ensemble confidence with model weighting"""
        if not scores:
            return 0.0
        
        # Weight different model types
        model_weights = {
            'isolation_forest': 1.2,
            'random_forest': 1.0,
            'svm': 0.9,
            'neural_network': 1.1
        }
        
        weighted_scores = []
        for model_name, score in predictions.items():
            if isinstance(score, (int, float)):
                weight = model_weights.get(model_name, 1.0)
                weighted_scores.append(score * weight)
        
        if weighted_scores:
            return min(sum(weighted_scores) / len(weighted_scores), 1.0)
        
        return 0.0
    
    def _create_basic_ensemble(self) -> Dict:
        """Create basic ensemble models if none exist"""
        try:
            from sklearn.ensemble import RandomForestClassifier, IsolationForest
            from sklearn.svm import OneClassSVM
            
            models = {}
            
            # Create basic models with default parameters
            models['isolation_forest'] = IsolationForest(
                contamination=0.1, 
                random_state=42,
                n_estimators=50
            )
            
            models['one_class_svm'] = OneClassSVM(
                gamma='scale',
                nu=0.1
            )
            
            # Train on synthetic data if no real data available
            synthetic_data = self._generate_synthetic_training_data()
            if len(synthetic_data) > 0:
                X = np.array(synthetic_data)
                
                # Fit models
                models['isolation_forest'].fit(X)
                models['one_class_svm'].fit(X)
                
                print(f"Created basic ensemble with {len(synthetic_data)} synthetic samples")
            
            return models
            
        except Exception as e:
            print(f"Failed to create basic ensemble: {e}")
            return {}
    
    def _generate_synthetic_training_data(self) -> List[List[float]]:
        """Generate synthetic training data for bootstrap ML models"""
        synthetic_data = []
        
        # Generate normal user patterns
        for _ in range(50):
            features = [
                np.random.normal(100, 30),  # UA length
                np.random.normal(15, 5),    # UA word count
                np.random.normal(3, 1),     # UA slash count
                np.random.normal(2, 1),     # UA parenthesis
                1,  # Has Mozilla
                np.random.choice([0, 1]),   # Has Chrome
                np.random.choice([0, 1]),   # Has Safari
                np.random.choice([0, 1]),   # Has Firefox
                np.random.normal(8, 2),     # Header count
                1, 1, 1, 1,  # Essential headers present
                0.3, 3,  # Layer confidences
                0.2, 2,
                0.1, 1,
                0.0, 0,
                0.0, 0,
                np.random.normal(50, 20),   # Mouse movements
                np.random.normal(3.5, 1),   # Mouse entropy
                np.random.normal(5, 2),     # Keyboard events
                np.random.normal(8000, 3000), # Time spent
                np.random.normal(3, 1),     # Click patterns
                np.random.normal(10, 5),    # Scroll events
            ]
            # Pad to 50 features
            while len(features) < 50:
                features.append(0.0)
            
            synthetic_data.append(features[:50])
        
        # Generate bot patterns
        for _ in range(20):
            features = [
                np.random.normal(50, 20),   # Shorter UA
                np.random.normal(8, 3),     # Fewer words
                np.random.normal(5, 2),     # More slashes
                np.random.normal(1, 1),     # Fewer parentheses
                np.random.choice([0, 1]),   # May not have Mozilla
                np.random.choice([0, 1]),   # May not have Chrome
                0, 0,  # Usually missing Safari/Firefox
                np.random.normal(5, 2),     # Fewer headers
                np.random.choice([0, 1]),   # Missing headers
                np.random.choice([0, 1]),
                np.random.choice([0, 1]),
                np.random.choice([0, 1]),
                0.8, 5,  # High layer confidences
                0.7, 4,
                0.6, 3,
                0.5, 2,
                0.4, 1,
                0,  # No mouse movements
                0,  # No entropy
                0,  # No keyboard
                np.random.normal(2000, 500), # Short time
                0,  # No clicks
                0,  # No scrolling
            ]
            # Pad to 50 features
            while len(features) < 50:
                features.append(0.0)
            
            synthetic_data.append(features[:50])
        
        return synthetic_data
    
    def _calculate_risk_level(self, confidence: float, layers: Dict) -> str:
        """Calculate risk level based on confidence and detection methods"""
        if confidence >= 0.9:
            return 'critical'
        elif confidence >= 0.7:
            return 'high'
        elif confidence >= 0.5:
            return 'medium'
        elif confidence >= 0.3:
            return 'low'
        else:
            return 'minimal'
    
    def _recommend_action(self, confidence: float, layers: Dict) -> str:
        """Recommend action based on detection results"""
        if confidence >= 0.85:
            return 'block_immediately'
        elif confidence >= 0.7:
            return 'challenge_required'
        elif confidence >= 0.5:
            return 'monitor_closely'
        elif confidence >= 0.3:
            return 'log_for_analysis'
        else:
            return 'allow_with_tracking'
    
    def _log_advanced_detection(self, request_data: Dict, result: Dict):
        """Log comprehensive detection results"""
        try:
            with transaction.atomic():
                # Create main detection record
                detection = BotDetection.objects.create(
                    ip_address=request_data.get('ip_address', ''),
                    user_agent=request_data.get('user_agent', '')[:1000],  # Truncate long UAs
                    fingerprint=request_data.get('fingerprint', '')[:64],
                    is_bot=result['is_bot'],
                    confidence_score=result['confidence'],
                    url_path=request_data.get('url_path', '/')[:500],
                    http_method=request_data.get('method', 'GET')[:10],
                    referrer=request_data.get('referrer', '')[:500],
                    country_code=result['geo_info'].get('country', '')[:2],
                    city=result['geo_info'].get('city', '')[:100],
                    status='bot' if result['is_bot'] else 'clean',
                    response_time=request_data.get('response_time')
                )
                
                # Set JSON fields
                detection.set_detection_methods(result['methods'][:50])  # Limit methods
                detection.set_behavioral_data(request_data.get('behavioral_data', {}))
                
                # Truncate headers to prevent database issues
                headers = request_data.get('headers', {})
                truncated_headers = {
                    k[:100]: str(v)[:200] for k, v in headers.items()
                }
                detection.set_headers(truncated_headers)
                detection.save()
                
                # Log security event for high-confidence detections
                if result['is_bot'] and result['confidence'] >= 0.7:
                    SecurityLog.log_event(
                        event_type='bot_detected',
                        ip_address=request_data.get('ip_address', ''),
                        description=f"Advanced bot detection: {result['confidence']:.3f} confidence",
                        severity='high' if result['confidence'] >= 0.8 else 'medium',
                        user_agent=request_data.get('user_agent', '')[:500],
                        details={
                            'detection_id': str(detection.id),
                            'methods_count': len(result['methods']),
                            'risk_level': result.get('risk_level', 'unknown'),
                            'layers_triggered': list(result.get('detection_layers', {}).keys())
                        }
                    )
                
        except Exception as e:
            print(f"Failed to log advanced detection: {e}")
    
    def _execute_auto_response(self, ip_address: str, result: Dict, request_data: Dict):
        """Execute automated response actions"""
        try:
            confidence = result['confidence']
            risk_level = result.get('risk_level', 'unknown')
            
            # Auto-blacklist for very high confidence
            if confidence >= 0.9 or risk_level == 'critical':
                self._add_to_blacklist_advanced(ip_address, result, request_data)
            
            # Rate limiting for medium-high confidence
            elif confidence >= 0.7:
                self._apply_rate_limiting(ip_address, severity='strict')
            
            # Monitoring for medium confidence
            elif confidence >= 0.5:
                self._add_to_monitoring(ip_address, result)
                
        except Exception as e:
            print(f"Failed to execute auto-response: {e}")
    
    def _add_to_blacklist_advanced(self, ip_address: str, result: Dict, request_data: Dict):
        """Advanced blacklist addition with detailed metadata"""
        try:
            methods_summary = ', '.join(result['methods'][:5])  # Top 5 methods
            
            blacklist_entry, created = IPBlacklist.objects.get_or_create(
                ip_address=ip_address,
                defaults={
                    'reason': f'Advanced bot detection - {result.get("risk_level", "high")} risk',
                    'confidence_score': result['confidence'],
                    'detection_method': methods_summary[:100],
                    'user_agent': request_data.get('user_agent', '')[:500],
                    'fingerprint': request_data.get('fingerprint', '')[:64],
                    'country_code': result['geo_info'].get('country', '')[:2],
                }
            )
            
            if not created:
                # Update existing entry with higher confidence
                if blacklist_entry.confidence_score < result['confidence']:
                    blacklist_entry.confidence_score = result['confidence']
                    blacklist_entry.detection_method = methods_summary[:100]
                
                blacklist_entry.detection_count += 1
                blacklist_entry.save()
            
            # Clear cache
            cache.delete(f"blacklist_{ip_address}")
            
            # Log critical security event
            SecurityLog.log_event(
                event_type='ip_blocked',
                ip_address=ip_address,
                description=f'IP auto-blacklisted by advanced detection (confidence: {result["confidence"]:.3f})',
                severity='critical',
                user_agent=request_data.get('user_agent', '')[:500],
                details={
                    'confidence': result['confidence'],
                    'risk_level': result.get('risk_level'),
                    'detection_methods': result['methods'][:10],
                    'auto_action': True
                }
            )
            
        except Exception as e:
            print(f"Failed advanced blacklist addition: {e}")
    
    def _apply_rate_limiting(self, ip_address: str, severity: str = 'normal'):
        """Apply rate limiting to suspicious IPs"""
        try:
            # Set rate limit in cache
            limit_key = f"rate_limit_{severity}_{ip_address}"
            current_time = timezone.now()
            
            if severity == 'strict':
                # Very restrictive for suspicious IPs
                cache.set(limit_key, current_time, 3600)  # 1 hour
                limit_requests = 10
            else:
                cache.set(limit_key, current_time, 1800)  # 30 minutes
                limit_requests = 30
            
            # Log rate limiting action
            SecurityLog.log_event(
                event_type='rate_limit_applied',
                ip_address=ip_address,
                description=f'{severity.title()} rate limiting applied',
                severity='medium',
                details={
                    'severity': severity,
                    'limit': limit_requests,
                    'duration_minutes': 60 if severity == 'strict' else 30
                }
            )
            
        except Exception as e:
            print(f"Failed to apply rate limiting: {e}")
    
    def _add_to_monitoring(self, ip_address: str, result: Dict):
        """Add IP to enhanced monitoring"""
        try:
            monitor_key = f"monitor_{ip_address}"
            monitor_data = {
                'confidence': result['confidence'],
                'methods': result['methods'][:10],
                'risk_level': result.get('risk_level', 'medium'),
                'timestamp': timezone.now().isoformat()
            }
            
            cache.set(monitor_key, monitor_data, 7200)  # 2 hours
            
        except Exception as e:
            print(f"Failed to add to monitoring: {e}")
    
    def _load_ml_model(self):
        """Load primary ML model"""
        model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'primary_bot_detector.joblib')
        
        try:
            if os.path.exists(model_path):
                return joblib.load(model_path)
            else:
                # Create basic isolation forest if no model exists
                model = IsolationForest(contamination=0.1, random_state=42)
                
                # Train on synthetic data
                synthetic_data = self._generate_synthetic_training_data()
                if synthetic_data:
                    X = np.array(synthetic_data)
                    model.fit(X)
                    
                    # Save model
                    os.makedirs(os.path.dirname(model_path), exist_ok=True)
                    joblib.dump(model, model_path)
                    print("Created and saved primary ML model")
                
                return model
                
        except Exception as e:
            print(f"Failed to load primary ML model: {e}")
            return None
    
    def _load_scaler(self):
        """Load feature scaler"""
        scaler_path = os.path.join(settings.BASE_DIR, 'ml_models', 'feature_scaler.joblib')
        
        try:
            if os.path.exists(scaler_path):
                return joblib.load(scaler_path)
            else:
                scaler = StandardScaler()
                
                # Fit on synthetic data
                synthetic_data = self._generate_synthetic_training_data()
                if synthetic_data:
                    X = np.array(synthetic_data)
                    scaler.fit(X)
                    
                    # Save scaler
                    os.makedirs(os.path.dirname(scaler_path), exist_ok=True)
                    joblib.dump(scaler, scaler_path)
                    print("Created and saved feature scaler")
                
                return scaler
                
        except Exception as e:
            print(f"Failed to load scaler: {e}")
            return StandardScaler()
    
    def get_statistics(self) -> Dict:
        """Get comprehensive bot detection statistics"""
        now = timezone.now()
        
        # Time periods
        last_hour = now - timedelta(hours=1)
        last_24h = now - timedelta(hours=24)
        last_week = now - timedelta(days=7)
        
        # Recent stats
        stats_1h = BotDetection.objects.filter(timestamp__gte=last_hour).aggregate(
            total_requests=Count('id'),
            bot_detections=Count('id', filter=Q(is_bot=True)),
            avg_confidence=Avg('confidence_score'),
            unique_ips=Count('ip_address', distinct=True)
        )
        
        stats_24h = BotDetection.objects.filter(timestamp__gte=last_24h).aggregate(
            total_requests=Count('id'),
            bot_detections=Count('id', filter=Q(is_bot=True)),
            avg_confidence=Avg('confidence_score'),
            unique_ips=Count('ip_address', distinct=True)
        )
        
        # Overall stats
        overall_stats = {
            'total_detections': BotDetection.objects.count(),
            'total_bots_detected': BotDetection.objects.filter(is_bot=True).count(),
            'active_blacklist_entries': IPBlacklist.objects.filter(is_active=True).count(),
            'threat_intel_entries': ThreatIntelligence.objects.filter(is_active=True).count(),
        }
        
        # Detection method frequency
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
        
        return {
            'last_hour': stats_1h,
            'last_24_hours': stats_24h,
            'overall': overall_stats,
            'top_detection_methods': dict(top_methods),
            'system_health': {
                'ml_model_loaded': self.ml_model is not None,
                'ensemble_models_count': len(self.ensemble_models),
                'geoip_available': self.geoip_reader is not None,
            },
            'generated_at': now.isoformat()
        }
