// hooks/useBotDetection.ts
import { useEffect, useState, useCallback } from 'react';

interface BotDetectionResult {
  isBot: boolean;
  confidence: number;
  detectionMethods: string[];
  userAgent: string;
  fingerprint: string;
}

interface BehaviorMetrics {
  mouseMovements: number;
  clickPatterns: number[];
  scrollBehavior: number;
  keyboardEvents: number;
  touchEvents: number;
  focusEvents: number;
  timeSpent: number;
  pageVisibility: number;
}

export const useBotDetection = () => {
  const [detectionResult, setDetectionResult] = useState<BotDetectionResult>({
    isBot: false,
    confidence: 0,
    detectionMethods: [],
    userAgent: '',
    fingerprint: ''
  });

  const [behaviorMetrics, setBehaviorMetrics] = useState<BehaviorMetrics>({
    mouseMovements: 0,
    clickPatterns: [],
    scrollBehavior: 0,
    keyboardEvents: 0,
    touchEvents: 0,
    focusEvents: 0,
    timeSpent: 0,
    pageVisibility: 0
  });

  // Generate device fingerprint
  const generateFingerprint = useCallback(async (): Promise<string> => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.textBaseline = 'top';
      ctx.font = '14px Arial';
      ctx.fillText('Bot detection fingerprint', 2, 2);
    }
    
    const fingerprint = {
      userAgent: navigator.userAgent,
      language: navigator.language,
      platform: navigator.platform,
      cookieEnabled: navigator.cookieEnabled,
      doNotTrack: navigator.doNotTrack,
      hardwareConcurrency: navigator.hardwareConcurrency,
      maxTouchPoints: navigator.maxTouchPoints,
      screen: {
        width: screen.width,
        height: screen.height,
        colorDepth: screen.colorDepth,
        pixelDepth: screen.pixelDepth
      },
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      canvas: canvas.toDataURL(),
      webgl: getWebGLFingerprint(),
      plugins: Array.from(navigator.plugins).map(p => p.name).join(','),
      connection: (navigator as any).connection?.effectiveType || 'unknown'
    };

    return btoa(JSON.stringify(fingerprint)).slice(0, 32);
  }, []);

  // WebGL fingerprinting
  const getWebGLFingerprint = (): string => {
    try {
      const canvas = document.createElement('canvas');
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
      if (!gl) return 'no-webgl';

      const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
      return debugInfo 
        ? `${gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL)}_${gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)}`
        : 'no-debug-info';
    } catch {
      return 'webgl-error';
    }
  };

  // User agent analysis
  const analyzeUserAgent = (ua: string): { isBot: boolean; confidence: number; reasons: string[] } => {
    const reasons: string[] = [];
    let confidence = 0;

    // Known bot patterns
    const botPatterns = [
      /bot|crawler|spider|crawling/i,
      /facebook|facebookexternalhit/i,
      /twitter|twitterbot/i,
      /google|googlebot|googleother/i,
      /bing|bingbot/i,
      /yahoo|slurp/i,
      /baidu|baiduspider/i,
      /yandex|yandexbot/i,
      /selenium|phantomjs|headless/i,
      /curl|wget|python|java|ruby/i
    ];

    botPatterns.forEach(pattern => {
      if (pattern.test(ua)) {
        reasons.push(`Bot pattern detected: ${pattern.source}`);
        confidence += 0.3;
      }
    });

    // Suspicious characteristics
    if (ua.length < 50) {
      reasons.push('User agent too short');
      confidence += 0.2;
    }

    if (!/Mozilla/.test(ua) && !/Chrome/.test(ua) && !/Safari/.test(ua)) {
      reasons.push('Missing common browser identifiers');
      confidence += 0.25;
    }

    // Facebook bot specific detection
    if (/facebookexternalhit|facebot/i.test(ua)) {
      reasons.push('Facebook bot detected');
      confidence = 0.95;
    }

    return { 
      isBot: confidence > 0.5, 
      confidence: Math.min(confidence, 1), 
      reasons 
    };
  };

  // Browser feature detection
  const detectBrowserFeatures = (): { isBot: boolean; confidence: number; reasons: string[] } => {
    const reasons: string[] = [];
    let confidence = 0;

    // Check for missing APIs that real browsers have
    const expectedAPIs = [
      'localStorage',
      'sessionStorage',
      'indexedDB',
      'requestAnimationFrame',
      'getBoundingClientRect'
    ];

    expectedAPIs.forEach(api => {
      if (!(api in window)) {
        reasons.push(`Missing API: ${api}`);
        confidence += 0.15;
      }
    });

    // Check for webdriver
    if ('webdriver' in navigator && (navigator as any).webdriver) {
      reasons.push('WebDriver detected');
      confidence += 0.4;
    }

    // Check for automation indicators
    if ((window as any).callPhantom || (window as any)._phantom || (window as any).phantom) {
      reasons.push('PhantomJS detected');
      confidence += 0.5;
    }

    if ((window as any).__nightmare) {
      reasons.push('Nightmare.js detected');
      confidence += 0.5;
    }

    // Check for headless Chrome
    if (navigator.webdriver !== undefined || (window as any).chrome?.runtime?.onConnect === undefined) {
      reasons.push('Possible headless browser');
      confidence += 0.2;
    }

    return { 
      isBot: confidence > 0.4, 
      confidence: Math.min(confidence, 1), 
      reasons 
    };
  };

  // Behavioral analysis using ML-like scoring
  const analyzeBehavior = (metrics: BehaviorMetrics): { isBot: boolean; confidence: number; reasons: string[] } => {
    const reasons: string[] = [];
    let confidence = 0;

    // Mouse movement analysis
    if (metrics.mouseMovements === 0 && metrics.timeSpent > 5000) {
      reasons.push('No mouse movements detected');
      confidence += 0.3;
    }

    // Click pattern analysis
    if (metrics.clickPatterns.length > 0) {
      const avgTimeBetweenClicks = metrics.clickPatterns.reduce((a, b) => a + b, 0) / metrics.clickPatterns.length;
      if (avgTimeBetweenClicks < 100) {
        reasons.push('Suspiciously fast clicking');
        confidence += 0.25;
      }
    }

    // Scroll behavior
    if (metrics.scrollBehavior === 0 && metrics.timeSpent > 10000) {
      reasons.push('No scrolling behavior');
      confidence += 0.2;
    }

    // Keyboard events
    if (metrics.keyboardEvents === 0 && metrics.timeSpent > 15000) {
      reasons.push('No keyboard interactions');
      confidence += 0.15;
    }

    // Page visibility
    if (metrics.pageVisibility === 0) {
      reasons.push('Page never gained focus');
      confidence += 0.2;
    }

    // Perfect behavior (too regular)
    const totalInteractions = metrics.mouseMovements + metrics.keyboardEvents + metrics.touchEvents;
    if (totalInteractions === 0 && metrics.timeSpent > 3000) {
      reasons.push('Zero user interactions');
      confidence += 0.4;
    }

    return { 
      isBot: confidence > 0.3, 
      confidence: Math.min(confidence, 1), 
      reasons 
    };
  };

  // Report bot detection to backend
  const reportBot = async (result: BotDetectionResult) => {
    try {
      await fetch('/api/bot-detection', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          isBot: result.isBot,
          confidence: result.confidence,
          methods: result.detectionMethods,
          userAgent: result.userAgent,
          fingerprint: result.fingerprint,
          timestamp: new Date().toISOString(),
          url: window.location.href
        })
      });
    } catch (error) {
      console.error('Failed to report bot detection:', error);
    }
  };

  // Main detection function
  const runDetection = useCallback(async () => {
    const fingerprint = await generateFingerprint();
    const userAgent = navigator.userAgent;
    
    const uaAnalysis = analyzeUserAgent(userAgent);
    const featureAnalysis = detectBrowserFeatures();
    const behaviorAnalysis = analyzeBehavior(behaviorMetrics);

    // Combine all detection methods
    const allReasons = [
      ...uaAnalysis.reasons,
      ...featureAnalysis.reasons,
      ...behaviorAnalysis.reasons
    ];

    // Calculate weighted confidence score
    const weightedConfidence = (
      uaAnalysis.confidence * 0.4 +
      featureAnalysis.confidence * 0.3 +
      behaviorAnalysis.confidence * 0.3
    );

    const finalResult: BotDetectionResult = {
      isBot: weightedConfidence > 0.6 || uaAnalysis.confidence > 0.8,
      confidence: weightedConfidence,
      detectionMethods: allReasons,
      userAgent,
      fingerprint
    };

    setDetectionResult(finalResult);

    // Report if bot detected
    if (finalResult.isBot && finalResult.confidence > 0.7) {
      await reportBot(finalResult);
    }

    return finalResult;
  }, [behaviorMetrics, generateFingerprint]);

  // Behavior tracking
  useEffect(() => {
    const startTime = Date.now();
    let mouseMovements = 0;
    let keyboardEvents = 0;
    let touchEvents = 0;
    let focusEvents = 0;
    let scrollEvents = 0;
    let clickTimes: number[] = [];
    let pageVisible = document.visibilityState === 'visible';

    const handleMouseMove = () => mouseMovements++;
    const handleKeyboard = () => keyboardEvents++;
    const handleTouch = () => touchEvents++;
    const handleFocus = () => focusEvents++;
    const handleScroll = () => scrollEvents++;
    const handleClick = () => clickTimes.push(Date.now());
    const handleVisibility = () => {
      pageVisible = document.visibilityState === 'visible';
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('keydown', handleKeyboard);
    document.addEventListener('touchstart', handleTouch);
    document.addEventListener('focus', handleFocus);
    document.addEventListener('scroll', handleScroll);
    document.addEventListener('click', handleClick);
    document.addEventListener('visibilitychange', handleVisibility);

    const interval = setInterval(() => {
      const timeSpent = Date.now() - startTime;
      const clickPatterns = clickTimes.slice(-10).reduce((acc, curr, index, arr) => {
        if (index > 0) acc.push(curr - arr[index - 1]);
        return acc;
      }, [] as number[]);

      setBehaviorMetrics({
        mouseMovements,
        clickPatterns,
        scrollBehavior: scrollEvents,
        keyboardEvents,
        touchEvents,
        focusEvents,
        timeSpent,
        pageVisibility: pageVisible ? 1 : 0
      });
    }, 1000);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('keydown', handleKeyboard);
      document.removeEventListener('touchstart', handleTouch);
      document.removeEventListener('focus', handleFocus);
      document.removeEventListener('scroll', handleScroll);
      document.removeEventListener('click', handleClick);
      document.removeEventListener('visibilitychange', handleVisibility);
      clearInterval(interval);
    };
  }, []);

  // Run detection on mount and periodically
  useEffect(() => {
    const runInitialDetection = async () => {
      await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2s for behavior
      await runDetection();
    };

    runInitialDetection();

    const interval = setInterval(runDetection, 10000); // Check every 10s

    return () => clearInterval(interval);
  }, [runDetection]);

  return {
    detectionResult,
    behaviorMetrics,
    runDetection
  };
};