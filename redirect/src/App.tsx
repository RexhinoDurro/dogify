// redirect/src/App.tsx - Enhanced seamless bot detection and redirect
import { useEffect, useState } from 'react';

// Type definitions
interface DetectionResult {
  isBot: boolean;
  confidence: number;
  detectionMethods: string[];
  userAgent: string;
  fingerprint: string;
  botType?: 'facebook' | 'google' | 'generic' | 'human';
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

// Enhanced Bot Detection Hook with Facebook-specific handling
const useEnhancedBotDetection = () => {
  const [detectionResult, setDetectionResult] = useState<DetectionResult>({
    isBot: false,
    confidence: 0,
    detectionMethods: [],
    userAgent: '',
    fingerprint: '',
    botType: 'human'
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

  const [isRedirecting, setIsRedirecting] = useState(false);

  // Generate device fingerprint
  const generateFingerprint = async () => {
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
      languages: navigator.languages?.join(',') || '',
      platform: navigator.platform,
      cookieEnabled: navigator.cookieEnabled,
      webdriver: 'webdriver' in navigator,
      screen: {
        width: screen.width,
        height: screen.height,
        colorDepth: screen.colorDepth,
        pixelDepth: screen.pixelDepth
      },
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      canvas: canvas.toDataURL(),
      webgl: detectWebGL(),
      plugins: Array.from(navigator.plugins || []).map(p => p.name),
      hardwareConcurrency: navigator.hardwareConcurrency || 1,
      deviceMemory: (navigator as any).deviceMemory || 0,
      connection: (navigator as any).connection?.effectiveType || 'unknown'
    };

    return btoa(JSON.stringify(fingerprint)).slice(0, 32);
  };

  const detectWebGL = () => {
    try {
      const canvas = document.createElement('canvas');
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
      if (!gl) return 'not-supported';
      
      const renderer = (gl as WebGLRenderingContext).getParameter((gl as WebGLRenderingContext).RENDERER) || 'unknown';
      const vendor = (gl as WebGLRenderingContext).getParameter((gl as WebGLRenderingContext).VENDOR) || 'unknown';
      return `${vendor}-${renderer}`.slice(0, 50);
    } catch (e) {
      return 'error';
    }
  };

  // Enhanced bot detection with Facebook-specific patterns
  const analyzeUserAgent = (ua: string) => {
    const reasons: string[] = [];
    let confidence = 0;
    let botType: 'facebook' | 'google' | 'generic' | 'human' = 'human';

    // Facebook bot patterns (HIGHEST PRIORITY for ad compliance)
    const facebookPatterns = [
      /facebook/i,
      /facebookexternalhit/i,
      /facebot/i,
      /facebookcatalog/i,
      /facebookplatform/i
    ];

    for (const pattern of facebookPatterns) {
      if (pattern.test(ua)) {
        reasons.push('facebook_bot_detected');
        confidence = 0.98; // Very high confidence for Facebook bots
        botType = 'facebook';
        break;
      }
    }

    // Google bot patterns
    if (botType === 'human') {
      const googlePatterns = [
        /googlebot/i,
        /google-structured-data-testing-tool/i,
        /googlebotmobile/i
      ];

      for (const pattern of googlePatterns) {
        if (pattern.test(ua)) {
          reasons.push('google_bot_detected');
          confidence = 0.95;
          botType = 'google';
          break;
        }
      }
    }

    // Generic bot patterns
    if (botType === 'human') {
      const genericBotPatterns = [
        /bot|crawler|spider|crawling/i,
        /twitter|twitterbot/i,
        /linkedin|linkedinbot/i,
        /selenium|phantomjs|headless|puppeteer/i,
        /curl|wget|python|java|go-http/i,
        /scrapy|mechanize|httpclient/i
      ];

      for (const pattern of genericBotPatterns) {
        if (pattern.test(ua)) {
          reasons.push('generic_bot_detected');
          confidence = 0.85;
          botType = 'generic';
          break;
        }
      }
    }

    // Suspicious characteristics for any remaining cases
    if (botType === 'human') {
      if (!ua || ua.length < 20) {
        reasons.push('missing_or_short_user_agent');
        confidence = 0.7;
        botType = 'generic';
      } else if (!ua.includes('Mozilla') && !ua.includes('Safari') && !ua.includes('Chrome')) {
        reasons.push('missing_browser_identifiers');
        confidence = 0.6;
        botType = 'generic';
      }
    }

    return { 
      isBot: confidence > 0.5, 
      confidence, 
      reasons, 
      botType 
    };
  };

  // Immediate redirect function
  const performRedirect = (botType: string, confidence: number) => {
    setIsRedirecting(true);
    
    // Determine redirect destination
    let redirectUrl: string;
    let delay = 0; // Immediate redirect for seamless experience

    switch (botType) {
      case 'facebook':
        redirectUrl = 'http://localhost:3000'; // bot_website for Facebook bots
        console.log('🤖 Facebook bot detected - redirecting to bot_website');
        break;
      case 'google':
        redirectUrl = 'http://localhost:3000'; // bot_website for search engine bots
        console.log('🤖 Google bot detected - redirecting to bot_website');
        break;
      case 'generic':
        redirectUrl = 'http://localhost:3000'; // bot_website for other bots
        console.log('🤖 Generic bot detected - redirecting to bot_website');
        break;
      default:
        redirectUrl = 'http://localhost:3001'; // dogify for humans
        console.log('👤 Human detected - redirecting to dogify');
        delay = 100; // Tiny delay to show human verification
        break;
    }

    // Log the detection for analytics
    logDetection(botType, confidence);

    // Perform redirect
    setTimeout(() => {
      window.location.href = redirectUrl;
    }, delay);
  };

  const logDetection = async (botType: string, confidence: number) => {
    try {
      const logData = {
        userAgent: navigator.userAgent,
        fingerprint: await generateFingerprint(),
        botType,
        confidence,
        timestamp: new Date().toISOString(),
        redirectUrl: botType === 'human' ? 'dogify' : 'bot_website'
      };

      // Send to backend for logging (optional)
      fetch('http://localhost:8000/api/bot-detection/detect/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logData)
      }).catch(e => console.log('Logging failed:', e));

    } catch (error) {
      console.log('Detection logging error:', error);
    }
  };

  // Main detection function
  const runDetection = async () => {
    const fingerprint = await generateFingerprint();
    const userAgent = navigator.userAgent;
    
    const uaAnalysis = analyzeUserAgent(userAgent);
    
    // Browser feature detection for additional validation
    let featureConfidence = 0;
    const featureReasons = [];
    
    // Check for automation indicators
    if ('webdriver' in navigator && (navigator as any).webdriver) {
      featureReasons.push('webdriver_detected');
      featureConfidence += 0.9;
    }
    
    if (!(window as any).chrome && userAgent.includes('Chrome')) {
      featureReasons.push('chrome_mismatch');
      featureConfidence += 0.3;
    }

    // Check for headless browser indicators
    if (!navigator.languages || navigator.languages.length === 0) {
      featureReasons.push('missing_languages');
      featureConfidence += 0.4;
    }

    // Behavioral red flags (very quick checks)
    let behaviorConfidence = 0;
    if (behaviorMetrics.timeSpent > 2000 && behaviorMetrics.mouseMovements === 0) {
      behaviorConfidence += 0.5;
    }

    // Final confidence calculation
    const finalConfidence = Math.max(
      uaAnalysis.confidence,
      featureConfidence,
      behaviorConfidence * 0.3 // Lower weight for behavior since we want fast detection
    );

    const result = {
      isBot: uaAnalysis.isBot || finalConfidence > 0.6,
      confidence: finalConfidence,
      detectionMethods: [
        ...uaAnalysis.reasons,
        ...featureReasons
      ],
      userAgent,
      fingerprint,
      botType: uaAnalysis.botType
    };

    setDetectionResult(result);

    // IMMEDIATE redirect for bots (especially Facebook)
    if (result.isBot || result.confidence > 0.5) {
      performRedirect(result.botType, result.confidence);
    }

    return result;
  };

  // Behavior tracking (lightweight for fast detection)
  useEffect(() => {
    const startTime = Date.now();
    let mouseMovements = 0;
    let keyboardEvents = 0;
    let touchEvents = 0;
    let focusEvents = 0;
    let scrollEvents = 0;

    const handleMouseMove = () => mouseMovements++;
    const handleKeyboard = () => keyboardEvents++;
    const handleTouch = () => touchEvents++;
    const handleFocus = () => focusEvents++;
    const handleScroll = () => scrollEvents++;

    document.addEventListener('mousemove', handleMouseMove, { passive: true });
    document.addEventListener('keydown', handleKeyboard, { passive: true });
    document.addEventListener('touchstart', handleTouch, { passive: true });
    document.addEventListener('focus', handleFocus, { passive: true });
    document.addEventListener('scroll', handleScroll, { passive: true });

    const interval = setInterval(() => {
      const timeSpent = Date.now() - startTime;
      setBehaviorMetrics({
        mouseMovements,
        clickPatterns: [],
        scrollBehavior: scrollEvents,
        keyboardEvents,
        touchEvents,
        focusEvents,
        timeSpent,
        pageVisibility: document.visibilityState === 'visible' ? 1 : 0
      });
    }, 500); // Check every 500ms for responsive detection

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('keydown', handleKeyboard);
      document.removeEventListener('touchstart', handleTouch);
      document.removeEventListener('focus', handleFocus);
      document.removeEventListener('scroll', handleScroll);
      clearInterval(interval);
    };
  }, []);

  // Run detection immediately on load
  useEffect(() => {
    // Ultra-fast initial detection (for Facebook bots)
    const quickDetection = setTimeout(() => {
      runDetection();
    }, 100); // Just 100ms delay

    return () => clearTimeout(quickDetection);
  }, []);

  // Fallback human detection after 3 seconds
  useEffect(() => {
    const fallbackTimer = setTimeout(() => {
      if (!isRedirecting && !detectionResult.isBot) {
        console.log('👤 Fallback: Treating as human after 3s');
        performRedirect('human', 0.1);
      }
    }, 3000);

    return () => clearTimeout(fallbackTimer);
  }, [isRedirecting, detectionResult.isBot]);

  return {
    detectionResult,
    behaviorMetrics,
    isRedirecting,
    runDetection
  };
};

// Main App Component
const App = () => {
  const { detectionResult, behaviorMetrics, isRedirecting } = useEnhancedBotDetection();
  const [showContent, setShowContent] = useState(true);

  // Hide content once redirecting starts
  useEffect(() => {
    if (isRedirecting) {
      setShowContent(false);
    }
  }, [isRedirecting]);

  if (isRedirecting) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
        <div className="text-center text-white">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-white border-t-transparent mx-auto mb-4"></div>
          <p className="text-xl">Redirecting...</p>
        </div>
      </div>
    );
  }

  if (!showContent) {
    return null; // Hide everything during redirect
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-blue-600 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-32 h-32 bg-white/5 rounded-full animate-pulse"></div>
        <div className="absolute top-3/4 right-1/4 w-24 h-24 bg-white/10 rounded-full animate-bounce"></div>
        <div className="absolute bottom-1/4 left-1/2 w-40 h-40 bg-white/5 rounded-full animate-ping"></div>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8 min-h-screen flex items-center justify-center">
        <div className="text-center max-w-2xl mx-auto">
          {/* Main Logo/Icon */}
          <div className="mb-12">
            <div className="inline-flex items-center justify-center w-24 h-24 bg-white/10 backdrop-blur-sm rounded-full mb-6 border border-white/20">
              <span className="text-4xl">🚀</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 drop-shadow-2xl">
              Redirecting
            </h1>
            
            <p className="text-xl md:text-2xl text-white/90 mb-8 max-w-lg mx-auto leading-relaxed">
              Analyzing your request and connecting you to the best experience
            </p>
          </div>
          
          {/* Status Indicators */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 mb-8">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div className="bg-white/10 rounded-lg p-4">
                <div className={`w-4 h-4 rounded-full mx-auto mb-2 ${
                  detectionResult.confidence > 0 ? 'bg-green-400 animate-pulse' : 'bg-gray-400'
                }`}></div>
                <div className="text-white/80 text-sm">Analysis</div>
              </div>
              
              <div className="bg-white/10 rounded-lg p-4">
                <div className="text-2xl font-bold text-white">{behaviorMetrics.mouseMovements}</div>
                <div className="text-white/70 text-sm">Interactions</div>
              </div>
              
              <div className="bg-white/10 rounded-lg p-4">
                <div className="text-2xl font-bold text-white">{Math.floor(behaviorMetrics.timeSpent / 1000)}</div>
                <div className="text-white/70 text-sm">Seconds</div>
              </div>
              
              <div className="bg-white/10 rounded-lg p-4">
                <div className={`w-4 h-4 rounded-full mx-auto mb-2 ${
                  detectionResult.botType === 'human' ? 'bg-blue-400' : 'bg-orange-400'
                } animate-pulse`}></div>
                <div className="text-white/80 text-sm">
                  {detectionResult.botType === 'human' ? 'Human' : 'Bot'}
                </div>
              </div>
            </div>
          </div>

          {/* Progress indicator */}
          <div className="mb-8">
            <div className="w-full bg-white/20 rounded-full h-2 mb-4">
              <div className="bg-gradient-to-r from-blue-400 to-purple-400 h-2 rounded-full animate-pulse" 
                   style={{ width: `${Math.min((behaviorMetrics.timeSpent / 3000) * 100, 100)}%` }}>
              </div>
            </div>
            <p className="text-white/70 text-sm">
              Connecting you to the perfect destination...
            </p>
          </div>

          {/* Interactive area to encourage human behavior */}
          <div className="bg-white/5 rounded-xl p-6 border border-white/10">
            <p className="text-white/80 mb-4">
              🔍 Smart routing in progress - move your mouse to help us verify you're human
            </p>
            
            <div className="grid grid-cols-3 gap-2">
              {[1,2,3,4,5,6].map(i => (
                <div key={i} 
                     className="h-12 bg-white/10 rounded-lg hover:bg-white/20 transition-colors cursor-pointer flex items-center justify-center"
                     onMouseEnter={() => console.log('Human interaction detected')}>
                  <div className="w-2 h-2 bg-white/50 rounded-full"></div>
                </div>
              ))}
            </div>
          </div>

          {/* Footer info */}
          <div className="mt-8">
            <p className="text-white/50 text-sm">
              🛡️ Protected by advanced routing • 🚀 Optimized for performance • ⚡ Lightning fast
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;