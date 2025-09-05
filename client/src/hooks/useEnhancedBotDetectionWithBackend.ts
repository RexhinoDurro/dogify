// Fixed useEnhancedBotDetectionWithBackend.ts - Backend-first approach
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

  // Very minimal local detection - only check for obvious patterns
  const runMinimalLocalDetection = (): { isBot: boolean; confidence: number; methods: string[] } => {
    const userAgent = navigator.userAgent || '';
    const methods: string[] = [];
    let confidence = 0;

    // Only flag absolutely obvious automation tools
    const obviousAutomationPatterns = [
      /\bcurl\b/i,
      /\bwget\b/i,
      /python-requests/i,
      /\bselenium\b/i,
      /puppeteer/i,
      /playwright/i,
    ];

    for (const pattern of obviousAutomationPatterns) {
      if (pattern.test(userAgent)) {
        methods.push('obvious_automation_tool');
        confidence = 0.95;
        break;
      }
    }

    // Check for Facebook patterns
    const facebookPatterns = [
      /facebookexternalhit/i,
      /facebot/i,
      /facebookcatalog/i,
    ];

    for (const pattern of facebookPatterns) {
      if (pattern.test(userAgent)) {
        methods.push('facebook_bot');
        confidence = 0.95;
        break;
      }
    }

    // Check if it looks like a browser (strong indicator it's NOT a bot)
    const browserIndicators = [
      'Mozilla/', 'Chrome/', 'Safari/', 'Firefox/', 'Edge/',
      'Windows NT', 'Macintosh', 'Android', 'iPhone', 'iPad'
    ];

    const hasBrowserIndicators = browserIndicators.some(indicator => 
      userAgent.includes(indicator)
    );

    if (hasBrowserIndicators && confidence === 0) {
      // Strong browser indicators and no automation patterns = likely human
      confidence = 0.05; // Very low bot confidence
      methods.push('browser_detected');
    }

    return {
      isBot: confidence >= 0.8,
      confidence,
      methods
    };
  };

  // Generate basic fingerprint
  const generateBasicFingerprint = (): string => {
    const components = [
      `screen:${screen.width}x${screen.height}x${screen.colorDepth}`,
      `tz:${new Date().getTimezoneOffset()}`,
      `lang:${navigator.language}`,
      `ua_len:${navigator.userAgent.length}`,
    ];

    return btoa(components.join('|')).substring(0, 32);
  };

  // Backend communication - primary detection method
  const communicateWithBackend = async (): Promise<void> => {
    if (backendCommunicated.current) return;

    try {
      console.log('🔍 Starting backend-first bot detection...');
      
      const localDetection = runMinimalLocalDetection();
      const fingerprint = generateBasicFingerprint();

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
        // Backend blocked - but check the response
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
        
        // Trust the backend completely
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
        
        // On backend failure, use local detection but be very conservative
        setDetectionResult(prev => ({
          ...prev,
          backendVerified: false,
          backendResult: { 
            status: 'error',
            is_bot: localDetection.isBot,
            blocked: false, // Don't block on backend failure
            confidence: localDetection.confidence * 0.5, // Reduce confidence
            error: `HTTP ${response.status}` 
          },
          isBot: localDetection.isBot && localDetection.confidence >= 0.95, // Very high threshold
          confidence: localDetection.confidence * 0.5,
          shouldBlock: false, // Never block on backend failure
          detectionMethods: localDetection.methods,
          fingerprint: fingerprint
        }));
      }
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('❌ Backend communication error:', errorMessage);
      
      // On error, run local detection but be very conservative
      const localDetection = runMinimalLocalDetection();
      
      setDetectionResult(prev => ({
        ...prev,
        backendVerified: false,
        backendResult: { 
          status: 'error',
          is_bot: false, // Assume human on error
          blocked: false,
          confidence: 0.1,
          error: errorMessage 
        },
        isBot: localDetection.confidence >= 0.95, // Only if very obvious
        confidence: Math.min(localDetection.confidence * 0.3, 0.3), // Very low confidence
        shouldBlock: false, // Never block on error
        detectionMethods: localDetection.methods.length > 0 ? localDetection.methods : ['error_fallback'],
        fingerprint: generateBasicFingerprint()
      }));
    }
  };

  // Behavior tracking (simplified)
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

  // Detection lifecycle - backend first
  useEffect(() => {
    // Quick local check for obvious bots
    const quickCheck = setTimeout(async () => {
      const localDetection = runMinimalLocalDetection();
      
      // If obvious automation tool, communicate immediately
      if (localDetection.confidence >= 0.95) {
        console.log('⚡ Obvious automation detected, contacting backend immediately');
        await communicateWithBackend();
      }
    }, 500);

    // Main backend communication
    const mainDetection = setTimeout(async () => {
      if (!backendCommunicated.current) {
        console.log('🚀 Running main backend detection...');
        await communicateWithBackend();
      }
    }, 2000);

    // Fallback check
    const fallbackCheck = setTimeout(async () => {
      if (!backendCommunicated.current) {
        console.log('🔍 Running fallback detection check...');
        await communicateWithBackend();
      }
    }, 8000);

    // Final timeout - assume human if backend never responds
    detectionTimeoutRef.current = window.setTimeout(() => {
      if (!backendCommunicated.current) {
        console.log('⏰ Backend timeout - assuming human');
        setDetectionResult(prev => ({
          ...prev,
          backendVerified: false,
          backendResult: { 
            status: 'timeout',
            is_bot: false,
            blocked: false,
            confidence: 0.1,
            error: 'Backend timeout - assuming human'
          },
          isBot: false,
          confidence: 0.1,
          shouldBlock: false,
          detectionMethods: ['backend_timeout_assume_human']
        }));
      }
    }, 15000);

    return () => {
      clearTimeout(quickCheck);
      clearTimeout(mainDetection);
      clearTimeout(fallbackCheck);
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