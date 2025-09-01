# services/bot_detection_service.py - Advanced bot detection service
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

from .models import (
    BotDetection, IPBlacklist, BehavioralPattern, 
    RequestPattern, SecurityLog, ThreatIntelligence
)



class BotDetectionService:
    """Advanced bot detection service with ML capabilities"""
    
    def __init__(self):
        self.bot_patterns = [
            # Facebook bots (high priority)
            re.compile(r'facebook|facebookexternalhit|facebot', re.I),
            re.compile(r'facebookcatalog|facebookplatform', re.I),
            
            # Other social media bots
            re.compile(r'twitter|twitterbot|tweetmeme', re.I),
            re.compile(r'linkedin|linkedinbot', re.I),
            
            # Search engine bots
            re.compile(r'google|googlebot|googleother', re.I),
            re.compile(r'bing|bingbot|msnbot', re.I),
            re.compile(r'yahoo|slurp', re.I),
            re.compile(r'baidu|baiduspider', re.I),
            re.compile(r'yandex|yandexbot', re.I),
            
            # Generic bot patterns
            re.compile(r'bot|crawler|spider|scraper|crawl', re.I),
            re.compile(r'curl|wget|python|java|ruby|go-http', re.I),
            re.compile(r'headless|phantom|selenium|puppeteer', re.I),
            
            # Automation tools
            re.compile(r'automation|mechanize|scrapy', re.I),
            re.compile(r'httpclient|okhttp|apache-httpclient', re.I),
        ]
        
        self.suspicious_headers = {
            'missing_accept': 0.3,
            'missing_accept_language': 0.2,
            'missing_accept_encoding': 0.15,
            'automation_headers': 0.4,
            'unusual_order': 0.1
        }
        
        # Load GeoIP database
        self.geoip_reader = None
        try:
            geoip_path = getattr(settings, 'GEOIP_PATH', None)
            if geoip_path:
                self.geoip_reader = geoip2.database.Reader(
                    os.path.join(geoip_path, 'GeoLite2-City.mmdb')
                )
        except Exception as e:
            print(f"Failed to load GeoIP database: {e}")
        
        # Load or initialize ML model
        self.ml_model = self._load_ml_model()
        self.scaler = self._load_scaler()
    
    def detect_bot(self, request_data: Dict) -> Dict:
        """
        Main bot detection method
        Returns detection result with confidence score
        """
        ip_address = request_data.get('ip_address')
        user_agent = request_data.get('user_agent', '')
        headers = request_data.get('headers', {})
        behavioral_data = request_data.get('behavioral_data', {})
        
        # Quick blacklist check
        if IPBlacklist.is_blacklisted(ip_address):
            return {
                'is_bot': True,
                'confidence': 1.0,
                'reason': 'IP blacklisted',
                'methods': ['blacklist_check']
            }
        
        detection_methods = []
        confidence_scores = []
        
        # 1. User Agent Analysis
        ua_result = self._analyze_user_agent(user_agent)
        if ua_result['confidence'] > 0:
            detection_methods.extend(ua_result['methods'])
            confidence_scores.append(ua_result['confidence'])
        
        # 2. Header Analysis
        header_result = self._analyze_headers(headers)
        if header_result['confidence'] > 0:
            detection_methods.extend(header_result['methods'])
            confidence_scores.append(header_result['confidence'])
        
        # 3. Request Pattern Analysis
        if ip_address is None:
            return {
                'confidence': 0,
                'methods': ['missing_ip_address'],
                'details': 'IP address is missing'
            }
        pattern_result = self._analyze_request_patterns(ip_address)
        if pattern_result['confidence'] > 0:
            detection_methods.extend(pattern_result['methods'])
            confidence_scores.append(pattern_result['confidence'])
        
        # 4. Behavioral Analysis
        behavior_result = None
        if behavioral_data:
            behavior_result = self._analyze_behavioral_data(behavioral_data)
            if behavior_result['confidence'] > 0:
                detection_methods.extend(behavior_result['methods'])
                confidence_scores.append(behavior_result['confidence'])
        
        # 5. Threat Intelligence Check
        threat_result = self._check_threat_intelligence(ip_address)
        if threat_result['confidence'] > 0:
            detection_methods.extend(threat_result['methods'])
            confidence_scores.append(threat_result['confidence'])
        
        # 6. ML Model Prediction
        ml_result = self._ml_predict(request_data)
        if ml_result['confidence'] > 0:
            detection_methods.extend(ml_result['methods'])
            confidence_scores.append(ml_result['confidence'])
        
        # Calculate final confidence score
        final_confidence = self._calculate_weighted_confidence(confidence_scores, detection_methods)
        is_bot = final_confidence >= 0.6
        
        # Geographic analysis
        geo_info = self._get_geo_info(ip_address)
        
        result = {
            'is_bot': is_bot,
            'confidence': final_confidence,
            'methods': detection_methods,
            'geo_info': geo_info,
            'analysis_details': {
                'user_agent_analysis': ua_result,
                'header_analysis': header_result,
                'pattern_analysis': pattern_result,
                'behavioral_analysis': behavior_result if behavioral_data else None,
                'threat_intelligence': threat_result,
                'ml_prediction': ml_result
            }
        }
        
        # Log the detection
        self._log_detection(request_data, result)
        
        # Auto-blacklist if high confidence bot
        if is_bot and final_confidence >= 0.8:
            self._add_to_blacklist(ip_address, result, request_data)
        
        return result
    
    def _analyze_user_agent(self, user_agent: str) -> Dict:
        """Analyze user agent for bot patterns"""
        if not user_agent:
            return {
                'confidence': 0.7,
                'methods': ['missing_user_agent'],
                'details': 'No user agent provided'
            }
        
        methods = []
        confidence = 0
        
        # Check against known bot patterns
        for i, pattern in enumerate(self.bot_patterns):
            if pattern.search(user_agent):
                methods.append(f'bot_pattern_{i}')
                if i < 2:  # Facebook bots get highest confidence
                    confidence = max(confidence, 0.95)
                elif i < 5:  # Social media bots
                    confidence = max(confidence, 0.85)
                elif i < 10:  # Search engine bots
                    confidence = max(confidence, 0.9)
                else:  # Generic patterns
                    confidence = max(confidence, 0.7)
        
        # Check for suspicious characteristics
        if len(user_agent) < 20:
            methods.append('short_user_agent')
            confidence = max(confidence, 0.6)
        
        if len(user_agent) > 500:
            methods.append('excessively_long_user_agent')
            confidence = max(confidence, 0.4)
        
        # Check for missing common browser identifiers
        if not re.search(r'Mozilla|Chrome|Safari|Firefox|Edge', user_agent, re.I):
            methods.append('missing_browser_identifiers')
            confidence = max(confidence, 0.5)
        
        # Check for suspicious version patterns
        if re.search(r'(\d+\.){4,}', user_agent):  # Too many version numbers
            methods.append('suspicious_version_pattern')
            confidence = max(confidence, 0.3)
        
        return {
            'confidence': confidence,
            'methods': methods,
            'details': f'User agent: {user_agent[:100]}...' if len(user_agent) > 100 else user_agent
        }
    
    def _analyze_headers(self, headers: Dict) -> Dict:
        """Analyze HTTP headers for bot indicators"""
        methods = []
        confidence = 0
        
        # Convert header names to lowercase for comparison
        headers_lower = {k.lower(): v for k, v in headers.items()}
        
        # Check for missing common headers
        if 'accept' not in headers_lower:
            methods.append('missing_accept_header')
            confidence += self.suspicious_headers['missing_accept']
        elif not headers_lower['accept'].startswith('text/html'):
            methods.append('non_browser_accept_header')
            confidence += 0.4
        
        if 'accept-language' not in headers_lower:
            methods.append('missing_accept_language')
            confidence += self.suspicious_headers['missing_accept_language']
        
        if 'accept-encoding' not in headers_lower:
            methods.append('missing_accept_encoding')
            confidence += self.suspicious_headers['missing_accept_encoding']
        elif 'gzip' not in headers_lower['accept-encoding']:
            methods.append('missing_gzip_support')
            confidence += 0.2
        
        # Check for automation-specific headers
        automation_headers = [
            'x-requested-with', 'x-forwarded-for', 'x-real-ip',
            'x-cluster-client-ip', 'x-forwarded-proto'
        ]
        
        for header in automation_headers:
            if header in headers_lower:
                methods.append(f'automation_header_{header}')
                confidence += 0.1
        
        # Check header order (browsers have typical patterns)
        expected_order = ['host', 'user-agent', 'accept', 'accept-language', 'accept-encoding']
        actual_order = list(headers_lower.keys())[:5]
        
        order_score = 0
        for i, expected in enumerate(expected_order):
            if i < len(actual_order) and actual_order[i] == expected:
                order_score += 1
        
        if order_score < 3:  # Less than 3 headers in expected order
            methods.append('unusual_header_order')
            confidence += self.suspicious_headers['unusual_order']
        
        return {
            'confidence': min(confidence, 1.0),
            'methods': methods,
            'details': f'Headers analyzed: {len(headers)}'
        }
    
    def _analyze_request_patterns(self, ip_address: str) -> Dict:
        """Analyze request patterns for bot behavior"""
        cache_key = f"pattern_analysis_{ip_address}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        analysis = RequestPattern.analyze_patterns(ip_address, minutes=10)
        
        confidence = 0
        methods = []
        
        if analysis['suspicious']:
            methods.extend(analysis['reasons'])
            
            # Calculate confidence based on severity
            if analysis['request_count'] > 100:
                confidence += 0.6
            elif analysis['request_count'] > 50:
                confidence += 0.4
            
            if analysis.get('unique_endpoints', 0) > 30:
                confidence += 0.3
        
        result = {
            'confidence': min(confidence, 1.0),
            'methods': methods,
            'details': analysis
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, result, 300)
        return result
    
    def _analyze_behavioral_data(self, behavioral_data: Dict) -> Dict:
        """Analyze behavioral data for human-like patterns"""
        methods = []
        confidence = 0
        
        # Mouse movement analysis
        mouse_movements = behavioral_data.get('mouseMovements', 0)
        mouse_entropy = behavioral_data.get('mouseEntropy', 0)
        
        if mouse_movements == 0 and behavioral_data.get('timeSpent', 0) > 5000:
            methods.append('no_mouse_movement')
            confidence += 0.4
        elif mouse_entropy < 2.0:
            methods.append('low_mouse_entropy')
            confidence += 0.3
        
        # Click pattern analysis
        click_patterns = behavioral_data.get('clickPatterns', [])
        if click_patterns:
            avg_click_time = sum(click_patterns) / len(click_patterns)
            if avg_click_time < 50:  # Impossibly fast clicking
                methods.append('impossibly_fast_clicking')
                confidence += 0.5
            elif avg_click_time < 100:  # Very fast clicking
                methods.append('very_fast_clicking')
                confidence += 0.3
        
        # Scroll behavior
        scroll_behavior = behavioral_data.get('scrollBehavior', 0)
        if scroll_behavior == 0 and behavioral_data.get('timeSpent', 0) > 10000:
            methods.append('no_scrolling')
            confidence += 0.2
        
        # Keyboard events
        keyboard_events = behavioral_data.get('keyboardEvents', 0)
        if keyboard_events == 0 and behavioral_data.get('timeSpent', 0) > 15000:
            methods.append('no_keyboard_interaction')
            confidence += 0.15
        
        # Perfect behavior (too regular patterns)
        total_interactions = (
            mouse_movements + 
            keyboard_events + 
            behavioral_data.get('touchEvents', 0)
        )
        
        if total_interactions == 0 and behavioral_data.get('timeSpent', 0) > 3000:
            methods.append('zero_user_interactions')
            confidence += 0.6
        
        return {
            'confidence': min(confidence, 1.0),
            'methods': methods,
            'details': behavioral_data
        }
    
    def _check_threat_intelligence(self, ip_address: str) -> Dict:
        """Check IP against threat intelligence databases"""
        cache_key = f"threat_intel_{ip_address}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        threats = ThreatIntelligence.objects.filter(
            ip_address=ip_address,
            is_active=True
        )
        
        methods = []
        confidence = 0
        
        for threat in threats:
            methods.append(f'threat_intel_{threat.threat_type}')
            confidence = max(confidence, threat.confidence)
        
        result = {
            'confidence': confidence,
            'methods': methods,
            'details': [
                {
                    'type': t.threat_type,
                    'source': t.source,
                    'confidence': t.confidence
                } for t in threats
            ]
        }
        
        # Cache for 1 hour
        cache.set(cache_key, result, 3600)
        return result
    
    def _ml_predict(self, request_data: Dict) -> Dict:
        """Use ML model to predict bot probability"""
        if not self.ml_model:
            return {'confidence': 0, 'methods': [], 'details': 'ML model not available'}
        
        try:
            # Extract features for ML model
            features = self._extract_ml_features(request_data)
            
            # Normalize features
            features_scaled = self.scaler.transform([features])
            
            # Get prediction
            anomaly_score = self.ml_model.decision_function(features_scaled)[0]
            is_anomaly = self.ml_model.predict(features_scaled)[0] == -1
            
            # Convert anomaly score to confidence (0-1 range)
            confidence = max(0, min(1, (-anomaly_score + 0.5) / 2))
            
            methods = ['ml_isolation_forest'] if is_anomaly else []
            
            return {
                'confidence': confidence if is_anomaly else 0,
                'methods': methods,
                'details': {
                    'anomaly_score': float(anomaly_score),
                    'is_anomaly': is_anomaly,
                    'features_count': len(features)
                }
            }
        
        except Exception as e:
            return {
                'confidence': 0,
                'methods': [],
                'details': f'ML prediction error: {str(e)}'
            }
    
    def _extract_ml_features(self, request_data: Dict) -> List[float]:
        """Extract features for ML model"""
        features = []
        
        # User agent features
        user_agent = request_data.get('user_agent', '')
        features.extend([
            len(user_agent),  # Length
            len(user_agent.split()),  # Word count
            user_agent.count('/'),  # Slash count
            user_agent.count('('),  # Parenthesis count
            1 if re.search(r'Mozilla', user_agent) else 0,  # Has Mozilla
            1 if re.search(r'Chrome', user_agent) else 0,  # Has Chrome
            1 if re.search(r'Safari', user_agent) else 0,  # Has Safari
        ])
        
        # Header features
        headers = request_data.get('headers', {})
        features.extend([
            len(headers),  # Header count
            1 if 'accept' in headers else 0,
            1 if 'accept-language' in headers else 0,
            1 if 'accept-encoding' in headers else 0,
            1 if 'user-agent' in headers else 0,
        ])
        
        # Behavioral features
        behavioral = request_data.get('behavioral_data', {})
        features.extend([
            behavioral.get('mouseMovements', 0),
            behavioral.get('keyboardEvents', 0),
            behavioral.get('touchEvents', 0),
            behavioral.get('timeSpent', 0) / 1000,  # Convert to seconds
            behavioral.get('mouseEntropy', 0),
            len(behavioral.get('clickPatterns', [])),
            behavioral.get('scrollBehavior', 0),
        ])
        
        # Request pattern features
        ip_address = request_data.get('ip_address')
        recent_requests = BotDetection.objects.filter(
            ip_address=ip_address,
            timestamp__gte=timezone.now() - timedelta(hours=1)
        ).count()
        
        features.extend([
            recent_requests,
            request_data.get('response_time', 0),
        ])
        
        # Pad or truncate to ensure consistent feature count
        target_length = 20
        if len(features) < target_length:
            features.extend([0] * (target_length - len(features)))
        else:
            features = features[:target_length]
        
        return features
    
    def _calculate_weighted_confidence(self, scores: List[float], methods: List[str]) -> float:
        """Calculate weighted confidence score"""
        if not scores:
            return 0.0
        
        # Weight different detection methods
        method_weights = {
            'bot_pattern_0': 1.0,  # Facebook bots
            'bot_pattern_1': 1.0,  # Facebook bots
            'blacklist_check': 1.0,
            'ml_isolation_forest': 0.8,
            'threat_intel': 0.9,
            'impossibly_fast_clicking': 0.8,
            'zero_user_interactions': 0.7,
            'missing_user_agent': 0.6,
        }
        
        weighted_scores = []
        for i, score in enumerate(scores):
            method = methods[i] if i < len(methods) else 'unknown'
            weight = method_weights.get(method, 0.5)  # Default weight
            weighted_scores.append(score * weight)
        
        # Use maximum weighted score, not average (more conservative)
        return min(max(weighted_scores) if weighted_scores else 0, 1.0)
    
    def _get_geo_info(self, ip_address: str) -> Dict:
        """Get geographic information for IP address"""
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
            }
        except geoip2.errors.AddressNotFoundError:
            return {'country': 'Unknown'}
        except Exception as e:
            return {'error': str(e)}
    
    def _log_detection(self, request_data: Dict, result: Dict):
        """Log detection result to database"""
        try:
            with transaction.atomic():
                detection = BotDetection.objects.create(
                    ip_address=request_data['ip_address'],
                    user_agent=request_data.get('user_agent', ''),
                    fingerprint=request_data.get('fingerprint', ''),
                    is_bot=result['is_bot'],
                    confidence_score=result['confidence'],
                    detection_methods=result['methods'],
                    url_path=request_data.get('url_path', '/'),
                    http_method=request_data.get('method', 'GET'),
                    referrer=request_data.get('referrer', ''),
                    behavioral_data=request_data.get('behavioral_data', {}),
                    headers=request_data.get('headers', {}),
                    country_code=result['geo_info'].get('country', ''),
                    city=result['geo_info'].get('city', ''),
                    status='bot' if result['is_bot'] else 'clean',
                    response_time=request_data.get('response_time'),
                )
                
                # Log security event if bot detected
                if result['is_bot']:
                    SecurityLog.log_event(
                        event_type='bot_detected',
                        ip_address=request_data['ip_address'],
                        description=f"Bot detected with {result['confidence']:.2f} confidence",
                        severity='high' if result['confidence'] > 0.8 else 'medium',
                        user_agent=request_data.get('user_agent', ''),
                        details={
                            'detection_id': str(detection.id),
                            'methods': result['methods'],
                            'confidence': result['confidence']
                        }
                    )
        
        except Exception as e:
            print(f"Failed to log detection: {e}")
    
    def _add_to_blacklist(self, ip_address: str, result: Dict, request_data: Dict):
        """Add IP to blacklist"""
        try:
            blacklist_entry, created = IPBlacklist.objects.get_or_create(
                ip_address=ip_address,
                defaults={
                    'reason': 'Automated bot detection',
                    'confidence_score': result['confidence'],
                    'detection_method': ', '.join(result['methods'][:3]),
                    'user_agent': request_data.get('user_agent', ''),
                    'fingerprint': request_data.get('fingerprint', ''),
                    'country_code': result['geo_info'].get('country', ''),
                }
            )
            
            if not created:
                # Update existing entry
                blacklist_entry.detection_count += 1
                blacklist_entry.confidence_score = max(
                    blacklist_entry.confidence_score, 
                    result['confidence']
                )
                blacklist_entry.save()
            
            # Clear cache
            cache_key = f"blacklist_{ip_address}"
            cache.delete(cache_key)
            
            # Log security event
            SecurityLog.log_event(
                event_type='ip_blocked',
                ip_address=ip_address,
                description=f"IP automatically blacklisted (confidence: {result['confidence']:.2f})",
                severity='critical',
                user_agent=request_data.get('user_agent', ''),
                details={'methods': result['methods']}
            )
            
        except Exception as e:
            print(f"Failed to add IP to blacklist: {e}")
    
    def _load_ml_model(self):
        """Load or create ML model for bot detection"""
        model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'bot_detector.joblib')
        
        try:
            if os.path.exists(model_path):
                return joblib.load(model_path)
            else:
                # Create and train new model
                return self._train_new_model()
        except Exception as e:
            print(f"Failed to load ML model: {e}")
            return None
    
    def _load_scaler(self):
        """Load feature scaler"""
        scaler_path = os.path.join(settings.BASE_DIR, 'ml_models', 'scaler.joblib')
        
        try:
            if os.path.exists(scaler_path):
                return joblib.load(scaler_path)
            else:
                return StandardScaler()
        except Exception as e:
            print(f"Failed to load scaler: {e}")
            return StandardScaler()
    
    def _train_new_model(self):
        """Train new ML model using historical data"""
        try:
            # Get training data from recent detections
            detections = BotDetection.objects.filter(
                timestamp__gte=timezone.now() - timedelta(days=30)
            ).values(
                'user_agent', 'headers', 'behavioral_data', 
                'is_bot', 'ip_address', 'response_time'
            )[:1000]  # Limit to 1000 records
            
            if len(detections) < 50:  # Need minimum data
                print("Insufficient training data for ML model")
                return None
            
            # Extract features
            X = []
            for detection in detections:
                features = self._extract_ml_features({
                    'user_agent': detection['user_agent'],
                    'headers': detection['headers'],
                    'behavioral_data': detection['behavioral_data'],
                    'ip_address': detection['ip_address'],
                    'response_time': detection['response_time'] or 0,
                })
                X.append(features)
            
            X = np.array(X)
            
            # Train Isolation Forest (unsupervised anomaly detection)
            model = IsolationForest(
                contamination=0.1,  # Expect 10% to be bots
                random_state=42,
                n_estimators=100
            )
            
            # Fit scaler and model
            self.scaler.fit(X)
            X_scaled = self.scaler.transform(X)
            model.fit(X_scaled)
            
            # Save model and scaler
            os.makedirs(os.path.dirname(os.path.join(settings.BASE_DIR, 'ml_models', 'bot_detector.joblib')), exist_ok=True)
            joblib.dump(model, os.path.join(settings.BASE_DIR, 'ml_models', 'bot_detector.joblib'))
            joblib.dump(self.scaler, os.path.join(settings.BASE_DIR, 'ml_models', 'scaler.joblib'))
            
            print(f"Trained new ML model with {len(X)} samples")
            return model
            
        except Exception as e:
            print(f"Failed to train ML model: {e}")
            return None
    
    def retrain_model(self):
        """Retrain ML model with latest data"""
        print("Retraining ML model...")
        self.ml_model = self._train_new_model()
        return self.ml_model is not None
    
    def get_statistics(self) -> Dict:
        """Get bot detection statistics"""
        now = timezone.now()
        
        # Last 24 hours stats
        last_24h = now - timedelta(hours=24)
        stats_24h = BotDetection.objects.filter(timestamp__gte=last_24h).aggregate(
            total_requests=Count('id'),
            bot_detections=Count('id', filter=Q(is_bot=True)),
            avg_confidence=Avg('confidence_score'),
            unique_ips=Count('ip_address', distinct=True)
        )
        
        # Overall stats
        overall_stats = {
            'total_blacklisted_ips': IPBlacklist.objects.filter(is_active=True).count(),
            'total_detections': BotDetection.objects.count(),
            'total_bots_detected': BotDetection.objects.filter(is_bot=True).count(),
        }
        
        return {
            'last_24_hours': stats_24h,
            'overall': overall_stats,
            'ml_model_available': self.ml_model is not None,
            'geoip_available': self.geoip_reader is not None,
        }