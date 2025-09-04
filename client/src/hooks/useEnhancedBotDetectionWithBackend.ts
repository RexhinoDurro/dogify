// Complete useEnhancedBotDetectionWithBackend.ts - Fixed version
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
  methods?: string[];
  risk_level?: string;
  message?: string;
  error?: string;
}

interface BotPattern {
  pattern: RegExp;
  weight: number;
  category: string;
}

interface DetectionAnalysis {
  isBot: boolean;
  confidence: number;
  reasons: string[];
  isFacebookBot?: boolean;
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
  const detectionIntervalRef = useRef<number | null>(null);
  const backendCommunicated = useRef<boolean>(false);

  // Enhanced Facebook bot detection patterns
  const facebookBotPatterns: BotPattern[] = [
    // Official Facebook crawlers - HIGHEST PRIORITY
    { pattern: /facebookexternalhit/i, weight: 0.98, category: 'facebook_external_hit' },
    { pattern: /facebot/i, weight: 0.97, category: 'facebook_bot' },
    { pattern: /facebookcatalog/i, weight: 0.96, category: 'facebook_catalog' },
    { pattern: /facebook.*bot/i, weight: 0.95, category: 'facebook_generic_bot' },
    
    // Other social media crawlers
    { pattern: /twitterbot|twitter/i, weight: 0.94, category: 'twitter_bot' },
    { pattern: /linkedinbot|linkedin/i, weight: 0.93, category: 'linkedin_bot' },
    { pattern: /instagrambot|instagram/i, weight: 0.92, category: 'instagram_bot' },
    
    // Search engines
    { pattern: /googlebot|google/i, weight: 0.90, category: 'google_bot' },
    { pattern: /bingbot|bing/i, weight: 0.89, category: 'bing_bot' },
    
    // Automation tools - CRITICAL
    { pattern: /selenium|webdriver/i, weight: 0.99, category: 'selenium_automation' },
    { pattern: /puppeteer|playwright/i, weight: 0.98, category: 'puppeteer_automation' },
    { pattern: /phantomjs|headless/i, weight: 0.97, category: 'headless_browser' },
    
    // Script tools
    { pattern: /curl|wget/i, weight: 0.95, category: 'command_line_tool' },
    { pattern: /python-requests|python-urllib/i, weight: 0.94, category: 'python_script' },
    { pattern: /node.*fetch|axios/i, weight: 0.90, category: 'nodejs_script' },
    
    // Generic bot patterns
    { pattern: /\bbot\b|crawler|spider|scraper/i, weight: 0.85, category: 'generic_bot' }
  ];

  // Enhanced user agent analysis with Facebook focus
  const analyzeFacebookBotUA = (userAgent: string): DetectionAnalysis => {
    if (!userAgent) {
      return { 
        isBot: false, // Changed: Don't assume bot for missing UA
        confidence: 0.3, // Reduced penalty
        reasons: ['missing_user_agent'],
        isFacebookBot: false
      };
    }

    const reasons: string[] = [];
    let confidence = 0;
    let isFacebookBot = false;

    console.log('🔍 Analyzing User Agent:', userAgent.substring(0, 100) + '...');

    // Check Facebook patterns first
    for (const botPattern of facebookBotPatterns) {
      if (botPattern.pattern.test(userAgent)) {
        reasons.push(`${botPattern.category}_detected`);
        confidence = Math.max(confidence, botPattern.weight);
        
        // Special Facebook bot handling
        if (botPattern.category.includes('facebook')) {
          isFacebookBot = true;
          console.log(`🤖📘 Facebook bot detected: ${botPattern.category} in user agent`);
          
          // Facebook external hit is almost 100% certain
          if (botPattern.category === 'facebook_external_hit') {
            confidence = 0.98;
          }
        }
      }
    }

    // Additional Facebook-specific analysis
    if (userAgent.toLowerCase().includes('facebook')) {
      if (!userAgent.includes('Mobile') && !userAgent.includes('Android') && !userAgent.includes('iPhone')) {
        reasons.push('facebook_desktop_crawler');
        confidence = Math.max(confidence, 0.95);
        isFacebookBot = true;
      }
      
      // Facebook crawlers often have simplified user agents
      const words = userAgent.split(' ').length;
      if (words < 5) {
        reasons.push('facebook_simplified_ua');
        confidence = Math.max(confidence, 0.90);
        isFacebookBot = true;
      }
    }

    // Length analysis (more lenient)
    const uaLength = userAgent.length;
    if (uaLength < 20) {
      reasons.push('very_short_ua');
      confidence = Math.max(confidence, 0.6); // Reduced from 0.8
    }

    // Browser version analysis (more lenient)
    if (!userAgent.match(/Chrome\/[\d.]+|Firefox\/[\d.]+|Safari\/[\d.]+/)) {
      // Check if it has other browser indicators
      const browserIndicators = ['Mozilla', 'WebKit', 'Gecko', 'Edge', 'Opera'];
      const hasBrowserIndicator = browserIndicators.some(indicator => userAgent.includes(indicator));
      
      if (!hasBrowserIndicator) {
        reasons.push('missing_browser_indicators');
        confidence = Math.max(confidence, 0.4); // Reduced penalty
      }
    }

    return { 
      isBot: confidence > 0.7, // Increased threshold from 0.6 to 0.7
      confidence, 
      reasons,
      isFacebookBot
    };
  };

  // Generate comprehensive fingerprint
  const generateFingerprint = async (): Promise<string> => {
    const components: string[] = [];
    
    try {
      // Screen and display metrics
      components.push(`screen:${screen.width}x${screen.height}x${screen.colorDepth}`);
      components.push(`avail:${screen.availWidth}x${screen.availHeight}`);
      components.push(`pixel:${window.devicePixelRatio || 1}`);
      
      // Browser info
      components.push(`ua_length:${navigator.userAgent.length}`);
      components.push(`platform:${navigator.platform}`);
      components.push(`cores:${navigator.hardwareConcurrency || 0}`);
      components.push(`memory:${(navigator as any).deviceMemory || 0}`);
      
      // Language and locale
      components.push(`lang:${navigator.language}`);
      components.push(`langs:${navigator.languages?.length || 0}`);
      components.push(`tz:${new Date().getTimezoneOffset()}`);
      
      // Plugins and features
      components.push(`plugins:${navigator.plugins?.length || 0}`);
      components.push(`touch:${navigator.maxTouchPoints || 0}`);
      
      // Canvas fingerprint (key for bot detection)
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.textBaseline = 'alphabetic';
        ctx.fillStyle = '#f60';
        ctx.fillRect(125, 1, 62, 20);
        ctx.fillStyle = '#069';
        ctx.font = '11pt Arial';
        ctx.fillText('🤖 Bot Detection Test 2024 🔍', 2, 15);
        
        // Add more complex patterns
        ctx.beginPath();
        ctx.arc(50, 50, 20, 0, Math.PI * 2);
        ctx.strokeStyle = '#FF6B6B';
        ctx.stroke();
        
        const canvasData = canvas.toDataURL();
        try {
          const canvasHash = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canvasData));
          const canvasFingerprint = Array.from(new Uint8Array(canvasHash))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('')
            .substring(0, 16);
          components.push(`canvas:${canvasFingerprint}`);
          
          setBehaviorMetrics(prev => ({ ...prev, canvasFingerprint }));
        } catch (e) {
          components.push(`canvas:unavailable`);
        }
      }
      
      // WebGL fingerprint
      try {
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        if (gl) {
          const glContext = gl as WebGLRenderingContext;
          const renderer = glContext.getParameter(glContext.RENDERER) || 'unknown';
          const vendor = glContext.getParameter(glContext.VENDOR) || 'unknown';
          const webglInfo = `${vendor}-${renderer}`;
          const webglHash = btoa(webglInfo).substring(0, 16);
          components.push(`webgl:${webglHash}`);
          
          setBehaviorMetrics(prev => ({ 
            ...prev, 
            webglFingerprint: webglHash,
            webglSupport: true
          }));
        } else {
          components.push('webgl:unavailable');
          setBehaviorMetrics(prev => ({ ...prev, webglSupport: false }));
        }
      } catch {
        components.push('webgl:error');
        setBehaviorMetrics(prev => ({ ...prev, webglSupport: false }));
      }
      
      // Screen resolution
      const screenRes = `${screen.width}x${screen.height}`;
      components.push(`resolution:${screenRes}`);
      setBehaviorMetrics(prev => ({ ...prev, screenResolution: screenRes }));
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      components.push(`error:${errorMessage.substring(0, 20)}`);
    }
    
    const fullFingerprint = components.join('|');
    return btoa(fullFingerprint).substring(0, 64);
  };

  // Backend communication with enhanced error handling
  const communicateWithBackend = async (localResult: {
    isBot: boolean;
    confidence: number;
    methods: string[];
    fingerprint: string;
    isFacebookBot?: boolean;
  }): Promise<void> => {
    if (backendCommunicated.current) return;

    try {
      console.log('🔍 Communicating with Django backend...');
      
      // Use relative URL for nginx proxy setup
      const backendUrl = '/api/bot-detection/detect/';
      
      const requestData = {
        user_agent: navigator.userAgent,
        fingerprint: localResult.fingerprint,
        is_bot: localResult.isBot,
        confidence: localResult.confidence,
        methods: localResult.methods,
        behavioral: behaviorMetrics,
        timestamp: new Date().toISOString(),
        url_path: window.location.pathname,
        referrer: document.referrer,
        is_facebook_bot: localResult.isFacebookBot || false,
      };

      const response = await fetch(backendUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'User-Agent': navigator.userAgent, // Include user agent in headers
        },
        body: JSON.stringify(requestData)
      });

      console.log('📡 Backend response status:', response.status);
      backendCommunicated.current = true;

      if (response.status === 403) {
        // Backend blocked the request - but check why
        console.log('🚫 Backend blocked the request');
        let errorData: any = {};
        try {
          errorData = await response.json();
          console.log('🚫 Block reason:', errorData);
        } catch (e) {
          console.log('🚫 Could not parse block reason');
        }
        
        // Only treat as bot if the backend explicitly says it's a bot
        const backendSaysBot = errorData.is_bot === true || errorData.blocked === true;
        
        setDetectionResult(prev => ({
          ...prev,
          backendVerified: true,
          backendResult: { 
            status: 'blocked',
            is_bot: backendSaysBot,
            blocked: true, 
            confidence: backendSaysBot ? 0.95 : 0.3, // Lower confidence if not explicitly a bot
            ...errorData
          },
          shouldBlock: backendSaysBot,
          confidence: backendSaysBot ? Math.max(prev.confidence, 0.95) : Math.max(prev.confidence, 0.3),
          isBot: backendSaysBot || prev.isBot
        }));
        return;
      }

      if (response.ok) {
        const result: BackendResult = await response.json();
        console.log('✅ Backend verification result:', result);
        
        setDetectionResult(prev => ({
          ...prev,
          backendVerified: true,
          backendResult: result,
          shouldBlock: result.blocked || false,
          confidence: Math.max(prev.confidence, result.confidence || 0),
          isBot: prev.isBot || result.is_bot,
          isFacebookBot: prev.isFacebookBot || result.is_facebook_bot,
          showDogWebsite: result.show_dog_website
        }));
      } else {
        console.warn('⚠️ Backend verification failed:', response.status);
        // Don't mark as bot just because backend failed - this is critical!
        setDetectionResult(prev => ({
          ...prev,
          backendVerified: false,
          backendResult: { 
            status: 'error',
            is_bot: false, // Important: don't assume bot on error
            blocked: false,
            confidence: 0,
            error: `HTTP ${response.status}` 
          }
        }));
      }
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('❌ Backend communication error (this is OK for humans):', errorMessage);
      
      // Don't mark as bot due to backend failure - this is critical!
      setDetectionResult(prev => ({
        ...prev,
        backendVerified: false,
        backendResult: { 
          status: 'error',
          is_bot: false, // Important: don't assume bot on error
          blocked: false,
          confidence: 0,
          error: errorMessage 
        },
        // Keep original detection result, don't make it worse
        isBot: prev.confidence > 0.8 ? prev.isBot : false,
        confidence: prev.confidence > 0.8 ? prev.confidence : Math.max(prev.confidence * 0.5, 0.1)
      }));
    }
  };

  // Main detection function with more lenient human detection
  const runEnhancedDetection = async (): Promise<DetectionResult> => {
    try {
      const userAgent = navigator.userAgent;
      const fingerprint = await generateFingerprint();
      
      console.log('🔍 Running enhanced detection with backend integration...');
      
      // Run local detection first
      const uaAnalysis = analyzeFacebookBotUA(userAgent);
      
      // Simple environment checks (more lenient)
      const hasWebdriver = !!(window.navigator as any)?.webdriver;
      const hasPhantom = !!(window as any).callPhantom || !!(window as any)._phantom;
      const envConfidence = hasWebdriver ? 0.95 : hasPhantom ? 0.90 : 0;
      const envMethods = [];
      if (hasWebdriver) envMethods.push('webdriver_detected');
      if (hasPhantom) envMethods.push('phantom_detected');

      // Calculate local confidence (much more lenient)
      const localConfidence = Math.max(uaAnalysis.confidence, envConfidence);
      const allMethods = [...uaAnalysis.reasons, ...envMethods];

      const localResult = {
        isBot: localConfidence >= 0.8 || uaAnalysis.isFacebookBot || false, // Increased threshold
        confidence: localConfidence,
        methods: allMethods,
        fingerprint,
        riskLevel: localConfidence >= 0.9 ? 'critical' : 
                   localConfidence >= 0.7 ? 'high' : 
                   localConfidence >= 0.5 ? 'medium' : 'low',
        isFacebookBot: uaAnalysis.isFacebookBot
      };

      console.log('📊 Local detection result:', {
        isBot: localResult.isBot,
        confidence: Math.round(localResult.confidence * 100) + '%',
        isFacebookBot: localResult.isFacebookBot,
        methods: localResult.methods.length
      });

      // Update state with local result first
      const newDetectionResult: DetectionResult = {
        ...localResult,
        detectionMethods: allMethods,
        backendVerified: false,
        backendResult: null,
        shouldBlock: false // Don't block based on local detection alone for most cases
      };

      setDetectionResult(newDetectionResult);

      // Communicate with backend asynchronously (non-blocking for humans)
      try {
        await communicateWithBackend(localResult);
      } catch (backendError) {
        console.log('Backend communication failed, continuing with local detection');
        // Don't fail the whole process if backend is down
      }

      return newDetectionResult;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('❌ Detection error:', errorMessage);
      
      // On error, assume human to avoid false positives
      const safeResult: DetectionResult = {
        isBot: false,
        confidence: 0,
        detectionMethods: ['detection_error'],
        fingerprint: '',
        riskLevel: 'low',
        backendVerified: false,
        backendResult: null,
        shouldBlock: false
      };
      
      setDetectionResult(safeResult);
      return safeResult;
    }
  };

  // Enhanced behavior tracking (less aggressive)
  useEffect(() => {
    let mouseMovements = 0;
    let keyboardEvents = 0;
    let scrollEvents = 0;
    let touchEvents = 0;
    let focusEvents = 0;
    const clickTimings: number[] = [];
    const mouseVelocities: number[] = [];
    let lastMouseTime = 0;
    let lastMousePos = { x: 0, y: 0 };
    
    const handleMouseMove = (e: MouseEvent) => {
      const now = Date.now();
      mouseMovements++;
      
      // Calculate velocity if we have previous data
      if (lastMouseTime > 0) {
        const timeDiff = now - lastMouseTime;
        if (timeDiff > 0) {
          const distance = Math.sqrt(
            Math.pow(e.clientX - lastMousePos.x, 2) +
            Math.pow(e.clientY - lastMousePos.y, 2)
          );
          const velocity = distance / timeDiff;
          mouseVelocities.push(velocity);
          
          // Keep only recent velocities
          if (mouseVelocities.length > 50) {
            mouseVelocities.shift();
          }
        }
      }
      
      lastMouseTime = now;
      lastMousePos = { x: e.clientX, y: e.clientY };
      
      setBehaviorMetrics(prev => ({
        ...prev,
        mouseMovements: mouseMovements,
        mouseVelocity: [...mouseVelocities]
      }));
    };

    const handleKeyboard = (_e: KeyboardEvent) => {
      keyboardEvents++;
      setBehaviorMetrics(prev => ({
        ...prev,
        keyboardEvents: keyboardEvents
      }));
    };

    const handleScroll = (e: WheelEvent) => {
      scrollEvents++;
      setBehaviorMetrics(prev => ({
        ...prev,
        scrollBehavior: scrollEvents,
        scrollDelta: [...prev.scrollDelta, e.deltaY || 0].slice(-20)
      }));
    };

    const handleClick = (_e: MouseEvent) => {
      const now = Date.now();
      clickTimings.push(now);
      
      // Calculate click intervals
      const intervals: number[] = [];
      for (let i = 1; i < clickTimings.length; i++) {
        intervals.push(clickTimings[i] - clickTimings[i - 1]);
      }
      
      setBehaviorMetrics(prev => ({
        ...prev,
        clickTiming: [...clickTimings].slice(-20),
        clickPatterns: intervals.slice(-15)
      }));
    };

    const handleTouch = () => {
      touchEvents++;
      setBehaviorMetrics(prev => ({
        ...prev,
        touchEvents: touchEvents
      }));
    };

    const handleFocus = () => {
      focusEvents++;
      setBehaviorMetrics(prev => ({
        ...prev,
        focusEvents: focusEvents
      }));
    };

    const handleDeviceMotion = () => {
      setBehaviorMetrics(prev => ({
        ...prev,
        deviceMotion: true
      }));
    };

    const handleOrientationChange = () => {
      setBehaviorMetrics(prev => ({
        ...prev,
        orientationChange: true
      }));
    };

    // Add all event listeners with proper cleanup
    document.addEventListener('mousemove', handleMouseMove, { passive: true });
    document.addEventListener('keydown', handleKeyboard);
    document.addEventListener('wheel', handleScroll, { passive: true });
    document.addEventListener('click', handleClick);
    document.addEventListener('touchstart', handleTouch, { passive: true });
    window.addEventListener('focus', handleFocus);
    window.addEventListener('devicemotion', handleDeviceMotion);
    window.addEventListener('orientationchange', handleOrientationChange);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('keydown', handleKeyboard);
      document.removeEventListener('wheel', handleScroll);
      document.removeEventListener('click', handleClick);
      document.removeEventListener('touchstart', handleTouch);
      window.removeEventListener('focus', handleFocus);
      window.removeEventListener('devicemotion', handleDeviceMotion);
      window.removeEventListener('orientationchange', handleOrientationChange);
    };
  }, []);

  // Detection timing and lifecycle (much more lenient)
  useEffect(() => {
    let detectionRun = false;
    
    // Quick detection for obvious bots only
    const quickDetection = setTimeout(async () => {
      const userAgent = navigator.userAgent.toLowerCase();
      // Only trigger quick detection for very obvious bots
      if (userAgent.includes('facebookexternalhit') || 
          userAgent.includes('googlebot') || 
          userAgent.includes('bingbot') ||
          userAgent.startsWith('curl/') ||
          userAgent.startsWith('wget/')) {
        console.log('⚡ Quick bot detection for obvious bot');
        detectionRun = true;
        await runEnhancedDetection();
      }
    }, 500);

    // Main detection - give humans much more time
    const mainDetection = setTimeout(async () => {
      if (!detectionRun) {
        console.log('🚀 Running main detection...');
        detectionRun = true;
        await runEnhancedDetection();
      }
    }, 3000); // Increased from 1.5s to 3s

    // Periodic re-detection (less frequent to avoid spam)
    detectionIntervalRef.current = window.setInterval(async () => {
      if (!backendCommunicated.current && !detectionRun) {
        console.log('🔍 Running periodic detection check...');
        await runEnhancedDetection();
      }
    }, 8000); // Every 8 seconds instead of 5

    // Final safety check
    const finalCheck = setTimeout(async () => {
      if (!detectionRun && !backendCommunicated.current) {
        console.log('🔍 Running final safety detection check...');
        await runEnhancedDetection();
      }
    }, 10000);

    return () => {
      clearTimeout(quickDetection);
      clearTimeout(mainDetection);
      clearTimeout(finalCheck);
      if (detectionIntervalRef.current) {
        window.clearInterval(detectionIntervalRef.current);
      }
    };
  }, []);

  // Update time spent continuously
  useEffect(() => {
    const timer = setInterval(() => {
      setBehaviorMetrics(prev => ({
        ...prev,
        timeSpent: Date.now() - startTimeRef.current
      }));
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return {
    detectionResult,
    behaviorMetrics,
    runEnhancedDetection
  };
};

export default useEnhancedBotDetectionWithBackend;