// Fixed useEnhancedBotDetectionWithBackend.ts - Better bot detection
import { useEffect, useState, useRef } from 'react';

// Type definitions
export interface BehaviorMetrics {
  mouseMovements: number;
  mouseEntropy: number;
  clickPatterns: number[];
  scrollBehavior: number;
  keyboardEvents: number;
  touchEvents: number;
  focusEvents: number;
  timeSpent: number;
  mouseVelocity: number[];
  mouseAcceleration: number[];
  clickTiming: number[];
  scrollDelta: number[];
  deviceMotion: boolean;
  orientationChange: boolean;
  batteryLevel: number | null;
  connectionType: string | null;
  screenFingerprint: string | null;
  canvasFingerprint: string | null;
  audioFingerprint: string | null;
  webglFingerprint: string | null;
  screenResolution: string | null;
  timezoneOffset: number;
  webglSupport: boolean;
}

export interface DetectionResult {
  isBot: boolean;
  confidence: number;
  detectionMethods: string[];
  fingerprint: string;
  riskLevel: string;
  backendVerified: boolean;
  backendResult: BackendResult | null;
  shouldBlock: boolean;
  isFacebookBot?: boolean;
  showDogWebsite?: boolean;
}

interface BackendResult {
  status: string;
  is_bot: boolean;
  confidence: number;
  blocked: boolean;
  is_facebook_bot?: boolean;
  show_dog_website?: boolean;
  browser_detected?: boolean;
  browser_type?: string;
  methods?: string[];
  risk_level?: string;
  message?: string;
  error?: string;
}

const useEnhancedBotDetectionWithBackend = () => {
  const [detectionResult, setDetectionResult] = useState<DetectionResult>({
    isBot: false,
    confidence: 0,
    detectionMethods: [],
    fingerprint: '',
    riskLevel: 'low',
    backendVerified: false,
    backendResult: null,
    shouldBlock: false
  });

  const [behaviorMetrics, setBehaviorMetrics] = useState<BehaviorMetrics>({
    mouseMovements: 0,
    mouseEntropy: 0,
    clickPatterns: [],
    scrollBehavior: 0,
    keyboardEvents: 0,
    touchEvents: 0,
    focusEvents: 0,
    timeSpent: 0,
    mouseVelocity: [],
    mouseAcceleration: [],
    clickTiming: [],
    scrollDelta: [],
    deviceMotion: false,
    orientationChange: false,
    batteryLevel: null,
    connectionType: null,
    screenFingerprint: null,
    canvasFingerprint: null,
    audioFingerprint: null,
    webglFingerprint: null,
    screenResolution: null,
    timezoneOffset: new Date().getTimezoneOffset(),
    webglSupport: false,
  });

  const startTimeRef = useRef<number>(Date.now());
  const backendCommunicated = useRef<boolean>(false);
  const detectionTimeoutRef = useRef<number | null>(null);

  // Enhanced local detection with proper bot patterns
  const runEnhancedLocalDetection = (): { isBot: boolean; confidence: number; methods: string[] } => {
    const userAgent = navigator.userAgent || '';
    const methods: string[] = [];
    let confidence = 0;

    console.log('🔍 Running enhanced local detection...');
    console.log('📝 User Agent:', userAgent);

    // 1. Check for obvious automation tools (HIGH CONFIDENCE)
    const automationPatterns = [
      /\bcurl\b/i,
      /\bwget\b/i,
      /python-requests/i,
      /python-urllib/i,
      /\bselenium\b/i,
      /puppeteer/i,
      /playwright/i,
      /phantomjs/i,
      /scrapy/i,
      /mechanize/i,
      /bot.*test|test.*bot/i,
    ];

    for (const pattern of automationPatterns) {
      if (pattern.test(userAgent)) {
        methods.push('automation_tool_detected');
        confidence = Math.max(confidence, 0.95);
        console.log('🤖 Automation tool detected:', pattern);
        break;
      }
    }

    // 2. Check for social media bots
    const socialBotPatterns = [
      /facebookexternalhit/i,
      /facebot/i,
      /facebookcatalog/i,
      /twitterbot/i,
      /linkedinbot/i,
      /googlebot/i,
      /bingbot/i,
    ];

    for (const pattern of socialBotPatterns) {
      if (pattern.test(userAgent)) {
        methods.push('social_media_bot');
        confidence = Math.max(confidence, 0.9);
        console.log('🤖📱 Social media bot detected:', pattern);
        break;
      }
    }

    // 3. Check for generic bot patterns
    const genericBotPatterns = [
      /\bbot\b/i,
      /\bcrawler\b/i,
      /\bspider\b/i,
      /\bscraper\b/i,
      /monitoring/i,
      /check/i,
      /scan/i,
    ];

    for (const pattern of genericBotPatterns) {
      if (pattern.test(userAgent)) {
        methods.push('generic_bot_pattern');
        confidence = Math.max(confidence, 0.7);
        console.log('🤖 Generic bot pattern detected:', pattern);
        break;
      }
    }

    // 4. Check if user agent is missing or too short
    if (!userAgent || userAgent.length < 10) {
      methods.push('missing_or_short_user_agent');
      confidence = Math.max(confidence, 0.8);
      console.log('🚨 Missing or very short user agent');
    }

    // 5. Check for browser indicators (REDUCES confidence if present)
    const browserIndicators = [
      'mozilla', 'chrome', 'safari', 'firefox', 'edge', 'opera',
      'webkit', 'gecko', 'mobile', 'android', 'iphone', 'ipad',
      'windows nt', 'macintosh', 'linux'
    ];

    const userAgentLower = userAgent.toLowerCase();
    const hasBrowserIndicators = browserIndicators.some(indicator => 
      userAgentLower.includes(indicator)
    );

    if (hasBrowserIndicators) {
      // Check for multiple browser indicators (real browsers have multiple)
      const browserCount = browserIndicators.filter(indicator => 
        userAgentLower.includes(indicator)
      ).length;

      if (browserCount >= 3) {
        console.log('✅ Multiple browser indicators detected, reducing bot confidence');
        confidence = confidence * 0.3; // Significantly reduce confidence
        methods.push('browser_indicators_detected');
      }
    }

    // 6. Enhanced browser version check
    const versionPatterns = [
      /chrome\/[\d.]+/i,
      /firefox\/[\d.]+/i,
      /safari\/[\d.]+/i,
      /edge\/[\d.]+/i,
    ];

    const hasVersionPattern = versionPatterns.some(pattern => pattern.test(userAgent));
    if (hasVersionPattern && hasBrowserIndicators) {
      console.log('✅ Browser version pattern detected');
      confidence = confidence * 0.2; // Very strong reduction for version + browser indicators
      methods.push('browser_version_detected');
    }

    // 7. Check for complex user agent structure (browsers have complex UAs)
    if (userAgent.length > 50 && userAgent.includes('(') && userAgent.includes(')')) {
      console.log('✅ Complex user agent structure detected');
      confidence = confidence * 0.5; // Reduce confidence for complex structure
      methods.push('complex_ua_structure');
    }

    console.log('📊 Local detection results:', {
      confidence: confidence,
      methods: methods,
      hasBrowserIndicators: hasBrowserIndicators,
      userAgentLength: userAgent.length
    });

    return {
      isBot: confidence >= 0.6, // Adjusted threshold
      confidence,
      methods
    };
  };

  // Generate enhanced fingerprint
  const generateEnhancedFingerprint = (): string => {
    const components = [
      `screen:${screen.width}x${screen.height}x${screen.colorDepth}`,
      `tz:${new Date().getTimezoneOffset()}`,
      `lang:${navigator.language}`,
      `ua_len:${navigator.userAgent.length}`,
      `plugins:${navigator.plugins?.length || 0}`,
      `touch:${navigator.maxTouchPoints || 0}`,
    ];

    return btoa(components.join('|')).substring(0, 32);
  };

  // Backend communication with proper error handling
  const communicateWithBackend = async (): Promise<void> => {
    if (backendCommunicated.current) return;

    try {
      console.log('🔍 Starting enhanced backend detection...');
      
      const localDetection = runEnhancedLocalDetection();
      const fingerprint = generateEnhancedFingerprint();

      const requestData = {
        user_agent: navigator.userAgent,
        fingerprint: fingerprint,
        is_bot: localDetection.isBot,
        confidence: localDetection.confidence,
        methods: localDetection.methods,
        behavioral: behaviorMetrics,
        timestamp: new Date().toISOString(),
        url_path: window.location.pathname,
        referrer: document.referrer,
        page: window.location.href,
        headers: {
          'User-Agent': navigator.userAgent,
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Language': navigator.language,
        }
      };

      console.log('📡 Sending request to backend:', {
        localBot: localDetection.isBot,
        localConfidence: localDetection.confidence,
        methods: localDetection.methods
      });

      const response = await fetch('/api/bot-detection/detect/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      console.log('📡 Backend response status:', response.status);
      backendCommunicated.current = true;

      if (response.status === 403) {
        // Backend blocked - parse the response
        let blockData: any = {};
        try {
          blockData = await response.json();
          console.log('🚫 Backend blocked with data:', blockData);
        } catch (e) {
          console.log('🚫 Backend blocked without data');
        }
        
        setDetectionResult(prev => ({
          ...prev,
          backendVerified: true,
          backendResult: { 
            status: 'blocked',
            is_bot: blockData.is_bot ?? true,
            blocked: true, 
            confidence: blockData.confidence ?? 0.9,
            message: blockData.message || 'Access blocked by backend',
            ...blockData
          },
          isBot: blockData.is_bot ?? true,
          confidence: blockData.confidence ?? 0.9,
          shouldBlock: true,
          detectionMethods: blockData.methods || ['backend_blocked']
        }));
        return;
      }

      if (response.ok) {
        const result: BackendResult = await response.json();
        console.log('✅ Backend verification result:', result);
        
        // Trust the backend result
        setDetectionResult(prev => ({
          ...prev,
          backendVerified: true,
          backendResult: result,
          isBot: result.is_bot,
          confidence: result.confidence,
          shouldBlock: result.blocked || false,
          isFacebookBot: result.is_facebook_bot || false,
          showDogWebsite: result.show_dog_website || false,
          detectionMethods: result.methods || [],
          riskLevel: result.risk_level || 'low',
          fingerprint: fingerprint
        }));
      } else {
        console.warn('⚠️ Backend verification failed:', response.status);
        
        // On backend failure, use local detection with reduced confidence
        setDetectionResult(prev => ({
          ...prev,
          backendVerified: false,
          backendResult: { 
            status: 'error',
            is_bot: localDetection.isBot,
            blocked: false,
            confidence: localDetection.confidence * 0.7, // Reduce confidence on backend failure
            error: `HTTP ${response.status}` 
          },
          isBot: localDetection.isBot && localDetection.confidence >= 0.8, // Higher threshold
          confidence: localDetection.confidence * 0.7,
          shouldBlock: false, // Don't block on backend failure
          detectionMethods: localDetection.methods,
          fingerprint: fingerprint
        }));
      }
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('❌ Backend communication error:', errorMessage);
      
      // On error, run local detection but be conservative
      const localDetection = runEnhancedLocalDetection();
      
      setDetectionResult(prev => ({
        ...prev,
        backendVerified: false,
        backendResult: { 
          status: 'error',
          is_bot: localDetection.isBot,
          blocked: false,
          confidence: localDetection.confidence * 0.5, // Very conservative
          error: errorMessage 
        },
        isBot: localDetection.confidence >= 0.9, // Very high threshold on error
        confidence: Math.min(localDetection.confidence * 0.5, 0.5),
        shouldBlock: false,
        detectionMethods: localDetection.methods.length > 0 ? localDetection.methods : ['error_fallback'],
        fingerprint: generateEnhancedFingerprint()
      }));
    }
  };

  // Enhanced behavior tracking
  useEffect(() => {
    let mouseMovements = 0;
    let keyboardEvents = 0;
    let scrollEvents = 0;
    let touchEvents = 0;
    let focusEvents = 0;
    const clickTimings: number[] = [];
    
    const handleMouseMove = () => {
      mouseMovements++;
      setBehaviorMetrics(prev => ({ ...prev, mouseMovements }));
    };

    const handleKeyboard = () => {
      keyboardEvents++;
      setBehaviorMetrics(prev => ({ ...prev, keyboardEvents }));
    };

    const handleScroll = () => {
      scrollEvents++;
      setBehaviorMetrics(prev => ({ ...prev, scrollBehavior: scrollEvents }));
    };

    const handleClick = () => {
      const now = Date.now();
      clickTimings.push(now);
      setBehaviorMetrics(prev => ({
        ...prev,
        clickTiming: [...clickTimings].slice(-10),
        clickPatterns: clickTimings.length > 1 ? 
          clickTimings.slice(-10).map((t, i, arr) => i > 0 ? t - arr[i-1] : 0).slice(1) : []
      }));
    };

    const handleTouch = () => {
      touchEvents++;
      setBehaviorMetrics(prev => ({ ...prev, touchEvents }));
    };

    const handleFocus = () => {
      focusEvents++;
      setBehaviorMetrics(prev => ({ ...prev, focusEvents }));
    };

    // Add event listeners
    document.addEventListener('mousemove', handleMouseMove, { passive: true });
    document.addEventListener('keydown', handleKeyboard);
    document.addEventListener('wheel', handleScroll, { passive: true });
    document.addEventListener('click', handleClick);
    document.addEventListener('touchstart', handleTouch, { passive: true });
    window.addEventListener('focus', handleFocus);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('keydown', handleKeyboard);
      document.removeEventListener('wheel', handleScroll);
      document.removeEventListener('click', handleClick);
      document.removeEventListener('touchstart', handleTouch);
      window.removeEventListener('focus', handleFocus);
    };
  }, []);

  // Time tracking
  useEffect(() => {
    const timer = setInterval(() => {
      setBehaviorMetrics(prev => ({
        ...prev,
        timeSpent: Date.now() - startTimeRef.current
      }));
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // Detection lifecycle - immediate for obvious bots
  useEffect(() => {
    // Immediate check for obvious automation tools
    const immediateCheck = setTimeout(async () => {
      const localDetection = runEnhancedLocalDetection();
      
      console.log('⚡ Immediate detection results:', localDetection);
      
      // If very high confidence bot, communicate immediately
      if (localDetection.confidence >= 0.9) {
        console.log('⚡ Very high confidence bot detected, contacting backend immediately');
        await communicateWithBackend();
      }
    }, 100);

    // Quick check for medium confidence
    const quickCheck = setTimeout(async () => {
      if (!backendCommunicated.current) {
        const localDetection = runEnhancedLocalDetection();
        
        if (localDetection.confidence >= 0.7) {
          console.log('⚡ High confidence bot detected, contacting backend');
          await communicateWithBackend();
        }
      }
    }, 1000);

    // Main backend communication
    const mainDetection = setTimeout(async () => {
      if (!backendCommunicated.current) {
        console.log('🚀 Running main backend detection...');
        await communicateWithBackend();
      }
    }, 3000);

    // Final timeout - if no backend response, use local detection
    detectionTimeoutRef.current = window.setTimeout(() => {
      if (!backendCommunicated.current) {
        console.log('⏰ Backend timeout - using local detection only');
        
        const localDetection = runEnhancedLocalDetection();
        
        setDetectionResult(prev => ({
          ...prev,
          backendVerified: false,
          backendResult: { 
            status: 'timeout',
            is_bot: localDetection.isBot,
            blocked: false,
            confidence: localDetection.confidence * 0.8, // Reduce confidence on timeout
            error: 'Backend timeout - using local detection'
          },
          isBot: localDetection.isBot && localDetection.confidence >= 0.8,
          confidence: localDetection.confidence * 0.8,
          shouldBlock: false, // Don't block on timeout
          detectionMethods: localDetection.methods.length > 0 ? localDetection.methods : ['local_detection_only']
        }));
      }
    }, 10000);

    return () => {
      clearTimeout(immediateCheck);
      clearTimeout(quickCheck);
      clearTimeout(mainDetection);
      if (detectionTimeoutRef.current) {
        window.clearTimeout(detectionTimeoutRef.current);
      }
    };
  }, []);

  return {
    detectionResult,
    behaviorMetrics,
    runEnhancedDetection: communicateWithBackend
  };
};

export default useEnhancedBotDetectionWithBackend;