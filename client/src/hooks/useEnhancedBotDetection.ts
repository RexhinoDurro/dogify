// dogify/src/hooks/useEnhancedBotDetection.ts
// Enhanced bot detection hook with backend communication - TypeScript version
import { useEffect, useState, useRef } from 'react';

// Type definitions - EXPORTED for use in other components
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
}

interface BackendResult {
  status: string;
  is_bot: boolean;
  confidence: number;
  blocked: boolean;
  is_facebook_bot?: boolean;
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

interface BackendCommunicationResult {
  backendVerified: boolean;
  backendResult: BackendResult | null;
  shouldBlock: boolean;
}

const useEnhancedBotDetection = () => {
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
    webglFingerprint: null
  });

  const startTimeRef = useRef<number>(Date.now());
  const detectionIntervalRef = useRef<number | null>(null);

  // Enhanced Facebook bot detection patterns
  const facebookBotPatterns: BotPattern[] = [
    // Official Facebook crawlers - HIGHEST PRIORITY
    { pattern: /facebookexternalhit/i, weight: 0.98, category: 'facebook_external_hit' },
    { pattern: /facebot/i, weight: 0.97, category: 'facebook_bot' },
    { pattern: /facebookcatalog/i, weight: 0.96, category: 'facebook_catalog' },
    { pattern: /facebook.*bot/i, weight: 0.95, category: 'facebook_generic_bot' },
    
    // Social media crawlers
    { pattern: /twitterbot|twitter/i, weight: 0.94, category: 'twitter_bot' },
    { pattern: /linkedinbot|linkedin/i, weight: 0.93, category: 'linkedin_bot' },
    { pattern: /instagrambot|instagram/i, weight: 0.92, category: 'instagram_bot' },
    { pattern: /whatsapp/i, weight: 0.91, category: 'whatsapp_bot' },
    
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
        isBot: true, 
        confidence: 0.9, 
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

    // Length analysis
    const uaLength = userAgent.length;
    if (uaLength < 30) {
      reasons.push('extremely_short_ua');
      confidence = Math.max(confidence, 0.80);
    }

    // Missing browser version patterns
    if (!userAgent.match(/Chrome\/[\d.]+|Firefox\/[\d.]+|Safari\/[\d.]+/)) {
      reasons.push('missing_browser_version');
      confidence = Math.max(confidence, 0.60);
    }

    return { 
      isBot: confidence > 0.6, 
      confidence, 
      reasons,
      isFacebookBot
    };
  };

  // Enhanced environment detection
  const detectBotEnvironment = (): { confidence: number; reasons: string[] } => {
    const reasons: string[] = [];
    let confidence = 0;

    // Direct bot indicators
    if (typeof window !== 'undefined') {
      // Check for webdriver
      if ((window.navigator as any)?.webdriver) {
        reasons.push('webdriver_detected');
        confidence += 0.95;
        console.log('🤖 WebDriver detected');
      }

      // Check for phantom
      if ((window as any).callPhantom || (window as any)._phantom) {
        reasons.push('phantom_detected');
        confidence += 0.90;
        console.log('🤖 PhantomJS detected');
      }

      // Check for Node.js Buffer
      if ((window as any).Buffer) {
        reasons.push('nodejs_buffer_detected');
        confidence += 0.85;
        console.log('🤖 Node.js Buffer detected');
      }

      // Missing Chrome object but claims to be Chrome
      if (!(window as any).chrome && navigator.userAgent.includes('Chrome')) {
        reasons.push('missing_chrome_object');
        confidence += 0.60;
      }

      // Plugin analysis
      if (navigator.plugins?.length === 0 && !navigator.userAgent.includes('Mobile')) {
        reasons.push('no_plugins_desktop');
        confidence += 0.50;
      }

      // Viewport analysis
      if (window.outerHeight === 0 || window.outerWidth === 0) {
        reasons.push('zero_outer_dimensions');
        confidence += 0.70;
      }

      // Language checks
      if (!navigator.languages || navigator.languages.length === 0) {
        reasons.push('no_languages');
        confidence += 0.60;
      }

      // Hardware inconsistencies
      if (navigator.hardwareConcurrency && navigator.hardwareConcurrency > 16) {
        reasons.push('excessive_cpu_cores');
        confidence += 0.30;
      }
    }

    return { confidence: Math.min(confidence, 1.0), reasons };
  };

  // Backend communication with enhanced error handling
  const communicateWithBackend = async (detectionData: {
    isBot: boolean;
    confidence: number;
    methods: string[];
    fingerprint: string;
    riskLevel: string;
  }): Promise<BackendCommunicationResult> => {
    try {
      console.log('🔍 Communicating with Django backend...', {
        confidence: detectionData.confidence,
        methods: detectionData.methods.length,
        isBot: detectionData.isBot
      });
      
      const requestData = {
        user_agent: navigator.userAgent,
        fingerprint: detectionData.fingerprint,
        is_bot: detectionData.isBot,
        confidence: detectionData.confidence,
        methods: detectionData.methods,
        behavioral: behaviorMetrics,
        timestamp: new Date().toISOString(),
        page: window.location.href,
        referrer: document.referrer,
        url_path: window.location.pathname,
        http_method: 'GET',
        risk_level: detectionData.riskLevel,
        headers: {
          'User-Agent': navigator.userAgent,
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Language': navigator.language,
          'Accept-Encoding': 'gzip, deflate'
        }
      };

      const response = await fetch('http://localhost:8000/api/bot-detection/detect/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(requestData)
      });

      console.log('📡 Backend response status:', response.status);

      if (response.status === 403) {
        // Backend blocked the request
        console.log('🚫 Backend blocked the request');
        let errorData: any = {};
        try {
          errorData = await response.json();
          console.log('🚫 Block reason:', errorData);
        } catch (e) {
          console.log('🚫 Could not parse block reason');
        }
        
        return {
          backendVerified: true,
          backendResult: { 
            status: 'blocked',
            is_bot: true,
            blocked: true, 
            confidence: 0.95,
            ...errorData
          },
          shouldBlock: true
        };
      }

      if (response.ok) {
        const result: BackendResult = await response.json();
        console.log('✅ Backend verification result:', result);
        
        return {
          backendVerified: true,
          backendResult: result,
          shouldBlock: result.blocked || (result.is_bot && result.confidence >= 0.7)
        };
      } else {
        console.warn('⚠️ Backend verification failed:', response.status, response.statusText);
        return {
          backendVerified: false,
          backendResult: { 
            status: 'error',
            is_bot: false,
            blocked: false,
            confidence: 0,
            error: `HTTP ${response.status}` 
          },
          shouldBlock: false
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('❌ Backend communication error:', errorMessage);
      return {
        backendVerified: false,
        backendResult: { 
          status: 'error',
          is_bot: false,
          blocked: false,
          confidence: 0,
          error: errorMessage 
        },
        shouldBlock: false
      };
    }
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
        ctx.fillText('🤖 Facebook Bot Detection 2024 🔍', 2, 15);
        
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
          
          setBehaviorMetrics(prev => ({ ...prev, webglFingerprint: webglHash }));
        } else {
          components.push('webgl:unavailable');
        }
      } catch (e) {
        components.push('webgl:error');
      }
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      components.push(`error:${errorMessage.substring(0, 20)}`);
    }
    
    const fullFingerprint = components.join('|');
    return btoa(fullFingerprint).substring(0, 64);
  };

  // Analyze behavior patterns
  const analyzeBehavior = (): { confidence: number; reasons: string[] } => {
    const methods: string[] = [];
    let confidence = 0;
    
    const timeSpent = Date.now() - startTimeRef.current;
    setBehaviorMetrics(prev => ({ ...prev, timeSpent }));
    
    // Zero interaction analysis (key bot indicator)
    if (timeSpent > 3000 && behaviorMetrics.mouseMovements === 0) {
      methods.push('no_mouse_interaction');
      confidence += 0.50;
    }
    
    if (timeSpent > 5000 && behaviorMetrics.keyboardEvents === 0) {
      methods.push('no_keyboard_interaction');
      confidence += 0.40;
    }
    
    if (timeSpent > 2000 && behaviorMetrics.scrollBehavior === 0) {
      methods.push('no_scroll_interaction');
      confidence += 0.35;
    }
    
    // Very short visit time (common for crawlers)
    if (timeSpent > 1000 && timeSpent < 2000 && behaviorMetrics.mouseMovements === 0) {
      methods.push('quick_crawl_pattern');
      confidence += 0.60;
    }
    
    return { confidence: Math.min(confidence, 1.0), reasons: methods };
  };

  // Calculate risk level
  const calculateRiskLevel = (confidence: number): string => {
    if (confidence >= 0.9) return 'critical';
    if (confidence >= 0.7) return 'high';
    if (confidence >= 0.5) return 'medium';
    if (confidence >= 0.3) return 'low';
    return 'minimal';
  };

  // Main detection function
  const runEnhancedDetection = async (): Promise<DetectionResult> => {
    try {
      const userAgent = navigator.userAgent;
      const fingerprint = await generateFingerprint();
      
      console.log('🔍 Running enhanced detection...', { userAgent: userAgent.substring(0, 50) + '...' });
      
      // Run detection layers
      const uaAnalysis = analyzeFacebookBotUA(userAgent);
      const envAnalysis = detectBotEnvironment();
      const behaviorAnalysis = analyzeBehavior();

      // Calculate weighted confidence
      const localConfidence = Math.max(
        uaAnalysis.confidence * 0.5,  // User agent is most important
        envAnalysis.confidence * 0.3,  // Environment check
        behaviorAnalysis.confidence * 0.2  // Behavior (less reliable early on)
      );

      const allMethods = [
        ...uaAnalysis.reasons,
        ...envAnalysis.reasons,
        ...behaviorAnalysis.reasons
      ];

      const localResult = {
        isBot: localConfidence >= 0.6 || uaAnalysis.isFacebookBot || false,
        confidence: localConfidence,
        methods: allMethods,
        fingerprint,
        riskLevel: calculateRiskLevel(localConfidence),
        isFacebookBot: uaAnalysis.isFacebookBot
      };

      console.log('📊 Local detection result:', {
        isBot: localResult.isBot,
        confidence: Math.round(localResult.confidence * 100) + '%',
        isFacebookBot: localResult.isFacebookBot,
        methods: localResult.methods.length
      });

      // Communicate with backend for verification
      const backendResult = await communicateWithBackend(localResult);

      // Combine results
      const finalResult: DetectionResult = {
        isBot: localResult.isBot,
        confidence: backendResult.backendVerified && backendResult.backendResult?.confidence
          ? Math.max(localResult.confidence, backendResult.backendResult.confidence)
          : localResult.confidence,
        detectionMethods: allMethods,
        fingerprint,
        riskLevel: calculateRiskLevel(localResult.confidence),
        backendVerified: backendResult.backendVerified,
        backendResult: backendResult.backendResult,
        shouldBlock: backendResult.shouldBlock || localResult.isBot,
        isFacebookBot: localResult.isFacebookBot || backendResult.backendResult?.is_facebook_bot
      };

      console.log('✅ Final detection result:', {
        isBot: finalResult.isBot,
        confidence: Math.round(finalResult.confidence * 100) + '%',
        backendVerified: finalResult.backendVerified,
        shouldBlock: finalResult.shouldBlock,
        isFacebookBot: finalResult.isFacebookBot
      });

      setDetectionResult(finalResult);
      return finalResult;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('❌ Detection error:', errorMessage);
      return detectionResult; // Return current state on error
    }
  };

  // Enhanced behavior tracking
  useEffect(() => {
    const mousePositions: Array<{x: number; y: number; time: number}> = [];
    let lastMouseTime = 0;
    
    const handleMouseMove = (e: MouseEvent) => {
      const now = Date.now();
      mousePositions.push({ x: e.clientX, y: e.clientY, time: now });
      if (mousePositions.length > 100) mousePositions.shift();
      
      // Calculate velocity if we have previous position
      if (lastMouseTime > 0) {
        const timeDiff = now - lastMouseTime;
        if (timeDiff > 0) {
          const prevPos = mousePositions[mousePositions.length - 2];
          if (prevPos) {
            const velocity = Math.sqrt(
              Math.pow(e.clientX - prevPos.x, 2) +
              Math.pow(e.clientY - prevPos.y, 2)
            ) / timeDiff;
            
            setBehaviorMetrics(prev => ({
              ...prev,
              mouseVelocity: [...prev.mouseVelocity.slice(-19), velocity]
            }));
          }
        }
      }
      lastMouseTime = now;
      
      setBehaviorMetrics(prev => ({
        ...prev,
        mouseMovements: prev.mouseMovements + 1
      }));
    };

    const handleClick = () => {
      const now = Date.now();
      setBehaviorMetrics(prev => {
        const newClickTiming = [...prev.clickTiming, now];
        const intervals: number[] = [];
        for (let i = 1; i < newClickTiming.length; i++) {
          intervals.push(newClickTiming[i] - newClickTiming[i - 1]);
        }
        return {
          ...prev,
          clickTiming: newClickTiming.slice(-20),
          clickPatterns: intervals.slice(-15)
        };
      });
    };

    const handleKeyboard = () => {
      setBehaviorMetrics(prev => ({
        ...prev,
        keyboardEvents: prev.keyboardEvents + 1
      }));
    };

    const handleScroll = (e: WheelEvent) => {
      setBehaviorMetrics(prev => ({
        ...prev,
        scrollBehavior: prev.scrollBehavior + 1,
        scrollDelta: [...prev.scrollDelta.slice(-19), e.deltaY || 0]
      }));
    };

    const handleTouch = () => {
      setBehaviorMetrics(prev => ({
        ...prev,
        touchEvents: prev.touchEvents + 1
      }));
    };

    const handleFocus = () => {
      setBehaviorMetrics(prev => ({
        ...prev,
        focusEvents: prev.focusEvents + 1
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

    // Add all event listeners
    if (typeof window !== 'undefined') {
      document.addEventListener('mousemove', handleMouseMove, { passive: true });
      document.addEventListener('click', handleClick);
      document.addEventListener('keydown', handleKeyboard);
      document.addEventListener('wheel', handleScroll, { passive: true });
      document.addEventListener('touchstart', handleTouch, { passive: true });
      window.addEventListener('focus', handleFocus);
      window.addEventListener('devicemotion', handleDeviceMotion);
      window.addEventListener('orientationchange', handleOrientationChange);

      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('click', handleClick);
        document.removeEventListener('keydown', handleKeyboard);
        document.removeEventListener('wheel', handleScroll);
        document.removeEventListener('touchstart', handleTouch);
        window.removeEventListener('focus', handleFocus);
        window.removeEventListener('devicemotion', handleDeviceMotion);
        window.removeEventListener('orientationchange', handleOrientationChange);
      };
    }
  }, []);

  // Detection loop with backend communication
  useEffect(() => {
    // Quick initial detection for obvious bots
    const quickDetection = setTimeout(async () => {
      const userAgent = navigator.userAgent.toLowerCase();
      if (userAgent.includes('facebook') || userAgent.includes('facebot') || userAgent.includes('bot')) {
        console.log('⚡ Quick bot detection triggered');
        await runEnhancedDetection();
      }
    }, 500);

    // Full initial detection
    const initialDetection = setTimeout(async () => {
      console.log('🚀 Starting initial bot detection...');
      await runEnhancedDetection();
    }, 1500);

    // Periodic re-detection
    detectionIntervalRef.current = window.setInterval(async () => {
      await runEnhancedDetection();
    }, 4000);

    return () => {
      clearTimeout(quickDetection);
      clearTimeout(initialDetection);
      if (detectionIntervalRef.current) {
        window.clearInterval(detectionIntervalRef.current);
      }
    };
  }, []);

  return {
    detectionResult,
    behaviorMetrics,
    runEnhancedDetection
  };
};

export default useEnhancedBotDetection;