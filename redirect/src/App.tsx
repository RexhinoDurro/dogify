import { useEffect, useState } from 'react';

// Type definitions
interface DetectionResult {
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

interface BotProtectionProps {
  children: React.ReactNode;
  onBotDetected?: (result: DetectionResult) => void;
  strictMode?: boolean;
}

interface RedirectCountdownProps {
  targetUrl: string;
  delay: number;
  confidence: number;
}

// Extend Window interface for Chrome property
declare global {
  interface Window {
    chrome?: {
      runtime?: unknown;
    };
  }
}

// Bot Detection Hook
const useBotDetection = () => {
  const [detectionResult, setDetectionResult] = useState<DetectionResult>({
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
      platform: navigator.platform,
      cookieEnabled: navigator.cookieEnabled,
      screen: {
        width: screen.width,
        height: screen.height,
        colorDepth: screen.colorDepth
      },
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      canvas: canvas.toDataURL()
    };

    return btoa(JSON.stringify(fingerprint)).slice(0, 32);
  };

  // Analyze user agent
  const analyzeUserAgent = (ua: string) => {
    const reasons: string[] = [];
    let confidence = 0;

    const botPatterns = [
      /facebook|facebookexternalhit|facebot/i,
      /bot|crawler|spider|crawling/i,
      /twitter|twitterbot/i,
      /google|googlebot/i,
      /selenium|phantomjs|headless/i,
      /curl|wget|python|java/i
    ];

    botPatterns.forEach((pattern, index) => {
      if (pattern.test(ua)) {
        reasons.push(`Bot pattern detected: ${index}`);
        confidence += index === 0 ? 0.95 : 0.7; // Facebook bots get highest confidence
      }
    });

    if (ua.length < 50) {
      reasons.push('User agent too short');
      confidence += 0.3;
    }

    return { 
      isBot: confidence > 0.6, 
      confidence: Math.min(confidence, 1), 
      reasons 
    };
  };

  // Main detection function
  const runDetection = async () => {
    const fingerprint = await generateFingerprint();
    const userAgent = navigator.userAgent;
    
    const uaAnalysis = analyzeUserAgent(userAgent);
    
    // Browser feature detection
    let featureConfidence = 0;
    const featureReasons = [];
    
    if ('webdriver' in navigator && navigator.webdriver) {
      featureReasons.push('WebDriver detected');
      featureConfidence += 0.8;
    }
    
    if (!window.chrome?.runtime) {
      featureReasons.push('Missing Chrome runtime');
      featureConfidence += 0.3;
    }

    // Behavioral analysis
    let behaviorConfidence = 0;
    const behaviorReasons = [];
    
    if (behaviorMetrics.mouseMovements === 0 && behaviorMetrics.timeSpent > 3000) {
      behaviorReasons.push('No mouse movements');
      behaviorConfidence += 0.5;
    }
    
    if (behaviorMetrics.keyboardEvents === 0 && behaviorMetrics.timeSpent > 5000) {
      behaviorReasons.push('No keyboard interactions');
      behaviorConfidence += 0.3;
    }

    const finalConfidence = Math.max(
      uaAnalysis.confidence * 0.5,
      featureConfidence * 0.3,
      behaviorConfidence * 0.2
    );

    const result = {
      isBot: finalConfidence > 0.6,
      confidence: finalConfidence,
      detectionMethods: [
        ...uaAnalysis.reasons,
        ...featureReasons,
        ...behaviorReasons
      ],
      userAgent,
      fingerprint
    };

    setDetectionResult(result);
    return result;
  };

  // Behavior tracking
  useEffect(() => {
    const startTime = Date.now();
    let mouseMovements = 0;
    let keyboardEvents = 0;
    let touchEvents = 0;
    let focusEvents = 0;
    let scrollEvents = 0;
    let clickTimes: number[] = [];

    const handleMouseMove = () => mouseMovements++;
    const handleKeyboard = () => keyboardEvents++;
    const handleTouch = () => touchEvents++;
    const handleFocus = () => focusEvents++;
    const handleScroll = () => scrollEvents++;
    const handleClick = () => clickTimes.push(Date.now());

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('keydown', handleKeyboard);
    document.addEventListener('touchstart', handleTouch);
    document.addEventListener('focus', handleFocus);
    document.addEventListener('scroll', handleScroll);
    document.addEventListener('click', handleClick);

    const interval = setInterval(() => {
      const timeSpent = Date.now() - startTime;
      const clickPatterns = clickTimes.slice(-10).reduce((acc: number[], curr, index, arr) => {
        if (index > 0) acc.push(curr - arr[index - 1]);
        return acc;
      }, []);

      setBehaviorMetrics({
        mouseMovements,
        clickPatterns,
        scrollBehavior: scrollEvents,
        keyboardEvents,
        touchEvents,
        focusEvents,
        timeSpent,
        pageVisibility: document.visibilityState === 'visible' ? 1 : 0
      });
    }, 1000);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('keydown', handleKeyboard);
      document.removeEventListener('touchstart', handleTouch);
      document.removeEventListener('focus', handleFocus);
      document.removeEventListener('scroll', handleScroll);
      document.removeEventListener('click', handleClick);
      clearInterval(interval);
    };
  }, []);

  // Run detection periodically
  useEffect(() => {
    const initialDetection = setTimeout(() => {
      runDetection();
    }, 2000); // Wait 2s for behavior data

    const periodicDetection = setInterval(() => {
      runDetection();
    }, 10000); // Check every 10s

    return () => {
      clearTimeout(initialDetection);
      clearInterval(periodicDetection);
    };
  }, [behaviorMetrics]);

  return {
    detectionResult,
    behaviorMetrics,
    runDetection
  };
};

// Bot Protection Component
const BotProtection: React.FC<BotProtectionProps> = ({ children, onBotDetected, strictMode = false }) => {
  const { detectionResult, behaviorMetrics } = useBotDetection();
  const [isBlocked, setIsBlocked] = useState(false);
  const [showWarning, setShowWarning] = useState(false);

  useEffect(() => {
    if (detectionResult.isBot) {
      const threshold = strictMode ? 0.5 : 0.7;
      
      if (detectionResult.confidence >= threshold) {
        setIsBlocked(true);
        onBotDetected?.(detectionResult);
        
        // Report to backend
        reportBotDetection(detectionResult);
      } else if (detectionResult.confidence >= 0.4) {
        setShowWarning(true);
        setTimeout(() => setShowWarning(false), 5000);
      }
    }
  }, [detectionResult, strictMode, onBotDetected]);

  const reportBotDetection = async (result: DetectionResult) => {
    try {
      const response = await fetch('http://localhost:8000/api/bot-detection/detect/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...result,
          behavioral: behaviorMetrics,
          timestamp: new Date().toISOString(),
          page: window.location.href,
          referrer: document.referrer
        })
      });

      if (!response.ok) {
        console.warn('Failed to report bot detection');
      }
    } catch (error) {
      console.error('Failed to report bot:', error);
    }
  };

  if (isBlocked) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-500 to-pink-600 flex items-center justify-center">
        <div className="max-w-2xl mx-auto text-center p-8 bg-white/10 backdrop-blur-lg rounded-3xl border border-white/20">
          <div className="text-8xl mb-6">🤖</div>
          <h1 className="text-4xl font-bold text-white mb-6">
            Bot Detected
          </h1>
          <p className="text-xl text-white/90 mb-8">
            Our advanced security system has detected automated behavior.
            Redirecting to the main site...
          </p>
          
          <div className="bg-white/10 border border-white/20 rounded-2xl p-6 mb-8 text-left">
            <h3 className="text-lg font-semibold text-white mb-4">Detection Details:</h3>
            <div className="space-y-2 text-white/80">
              <p><strong>Confidence:</strong> {Math.round(detectionResult.confidence * 100)}%</p>
              <p><strong>Methods:</strong> {detectionResult.detectionMethods.slice(0, 3).join(', ')}</p>
              <p><strong>User Agent:</strong> {navigator.userAgent.substring(0, 100)}...</p>
            </div>
          </div>

          <RedirectCountdown 
            targetUrl="http://localhost:5173" 
            delay={3} 
            confidence={detectionResult.confidence}
          />
        </div>
      </div>
    );
  }

  return (
    <>
      {showWarning && (
        <div className="fixed top-4 right-4 bg-yellow-500/90 backdrop-blur-sm text-yellow-900 px-6 py-4 rounded-xl shadow-lg z-50 border border-yellow-400">
          <div className="flex items-center">
            <span className="text-2xl mr-3">⚠️</span>
            <div>
              <p className="font-bold">Security Alert</p>
              <p className="text-sm">Unusual activity detected</p>
            </div>
          </div>
        </div>
      )}
      
      <div className="bot-protected-content">
        {children}
      </div>
    </>
  );
};

// Redirect Countdown Component
const RedirectCountdown: React.FC<RedirectCountdownProps> = ({ targetUrl, delay }) => {
  const [countdown, setCountdown] = useState(delay);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev: number) => {
        if (prev <= 1) {
          window.location.href = targetUrl;
          return 0;
        }
        return prev - 1;
      });
      
      setProgress((prev: number) => prev + (100 / delay));
    }, 1000);

    return () => clearInterval(timer);
  }, [targetUrl, delay]);

  return (
    <div className="space-y-6">
      <div className="relative">
        <div className="w-full bg-white/20 rounded-full h-4">
          <div 
            className="bg-gradient-to-r from-blue-400 to-purple-500 h-4 rounded-full transition-all duration-1000"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-white font-bold text-sm">
            Redirecting in {countdown}s
          </span>
        </div>
      </div>
      
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button 
          onClick={() => window.location.href = targetUrl}
          className="bg-white text-red-600 px-8 py-3 rounded-full font-bold hover:bg-gray-100 transition-colors"
        >
          Redirect Now
        </button>
        <button 
          onClick={() => window.location.reload()}
          className="border-2 border-white text-white px-8 py-3 rounded-full font-bold hover:bg-white hover:text-red-600 transition-colors"
        >
          I'm Human - Retry
        </button>
      </div>
      
      <p className="text-white/70 text-sm">
        If you believe this is an error, please contact support or try refreshing the page.
      </p>
    </div>
  );
};

// Main App Component
const App = () => {
  const [showDebugInfo, setShowDebugInfo] = useState(false);
  const { detectionResult, behaviorMetrics } = useBotDetection();

  const handleBotDetected = (result: DetectionResult) => {
    console.warn('Bot detected:', result);
    // Additional analytics or logging can be added here
  };

  // Anti-debugging measures
  useEffect(() => {
    const handleContextMenu = (e: Event) => e.preventDefault();
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'F12' || 
          (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'J')) ||
          (e.ctrlKey && e.key === 'U')) {
        e.preventDefault();
      }
    };

    // Simple devtools detection
    let devtools = { open: false };
    const threshold = 160;

    const detectDevTools = () => {
      if (window.outerHeight - window.innerHeight > threshold || 
          window.outerWidth - window.innerWidth > threshold) {
        if (!devtools.open) {
          devtools.open = true;
          console.clear();
          console.warn('Developer tools detected');
        }
      } else {
        devtools.open = false;
      }
    };

    const devToolsInterval = setInterval(detectDevTools, 1000);

    document.addEventListener('contextmenu', handleContextMenu);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('contextmenu', handleContextMenu);
      document.removeEventListener('keydown', handleKeyDown);
      clearInterval(devToolsInterval);
    };
  }, []);

  return (
    <BotProtection onBotDetected={handleBotDetected} strictMode={true}>
      <div className="min-h-screen bg-gradient-to-br from-purple-600 via-blue-600 to-teal-500">
        <div className="container mx-auto px-4 py-8">
          {/* Security Status Bar */}
          <div className="mb-8 p-4 bg-white/10 backdrop-blur-lg rounded-xl border border-white/20">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={`w-4 h-4 rounded-full animate-pulse ${
                  detectionResult.confidence < 0.3 ? 'bg-green-400' :
                  detectionResult.confidence < 0.6 ? 'bg-yellow-400' : 'bg-red-400'
                }`}></div>
                <span className="text-white font-medium">
                  Security Status: {
                    detectionResult.confidence < 0.3 ? '✅ Verified Human' :
                    detectionResult.confidence < 0.6 ? '⚠️ Under Review' : '🚫 Bot Detected'
                  }
                </span>
              </div>
              <button
                onClick={() => setShowDebugInfo(!showDebugInfo)}
                className="text-white/80 hover:text-white text-sm bg-white/10 px-4 py-2 rounded-lg transition-colors"
              >
                {showDebugInfo ? 'Hide' : 'Show'} Debug
              </button>
            </div>
            
            {showDebugInfo && (
              <div className="mt-4 p-4 bg-black/20 rounded-lg text-white text-sm font-mono">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-bold mb-2">Detection Results:</h4>
                    <div>Bot Confidence: {(detectionResult.confidence * 100).toFixed(1)}%</div>
                    <div>Is Bot: {detectionResult.isBot ? 'Yes' : 'No'}</div>
                    <div>Methods: {detectionResult.detectionMethods.length}</div>
                  </div>
                  <div>
                    <h4 className="font-bold mb-2">Behavioral Metrics:</h4>
                    <div>Mouse Movements: {behaviorMetrics.mouseMovements}</div>
                    <div>Keyboard Events: {behaviorMetrics.keyboardEvents}</div>
                    <div>Time Spent: {(behaviorMetrics.timeSpent / 1000).toFixed(1)}s</div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Main Content */}
          <div className="text-center">
            <div className="mb-12">
              <div className="inline-flex items-center justify-center w-32 h-32 bg-white/10 backdrop-blur-lg rounded-full mb-8 border border-white/20">
                <span className="text-6xl">🛡️</span>
              </div>
              
              <h1 className="text-6xl md:text-8xl font-bold text-white mb-6 drop-shadow-2xl">
                Security Check
              </h1>
              
              <p className="text-xl md:text-2xl text-white/90 mb-8 max-w-3xl mx-auto leading-relaxed">
                Advanced bot protection system analyzing your visit. 
                Real humans will be redirected to the main site automatically.
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto mb-12">
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 hover:bg-white/15 transition-colors">
                <div className="text-4xl mb-4">🤖</div>
                <h3 className="text-white font-bold text-xl mb-4">AI Bot Detection</h3>
                <p className="text-white/80">
                  Machine learning powered detection with behavioral analysis and pattern recognition
                </p>
              </div>
              
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 hover:bg-white/15 transition-colors">
                <div className="text-4xl mb-4">🚫</div>
                <h3 className="text-white font-bold text-xl mb-4">Real-time Blocking</h3>
                <p className="text-white/80">
                  Instant blocking of detected bots with automatic IP blacklisting for repeat offenders
                </p>
              </div>
              
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 hover:bg-white/15 transition-colors">
                <div className="text-4xl mb-4">📊</div>
                <h3 className="text-white font-bold text-xl mb-4">Advanced Analytics</h3>
                <p className="text-white/80">
                  Comprehensive monitoring with threat intelligence and behavioral pattern analysis
                </p>
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 max-w-2xl mx-auto border border-white/20">
              <h2 className="text-2xl font-bold text-white mb-4">Human Verification</h2>
              <p className="text-white/90 mb-6">
                Move your mouse around and interact with this page to prove you're human.
                Bots will be automatically redirected.
              </p>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div className="bg-white/10 rounded-lg p-4">
                  <div className="text-2xl font-bold text-white">{behaviorMetrics.mouseMovements}</div>
                  <div className="text-white/70 text-sm">Mouse Moves</div>
                </div>
                <div className="bg-white/10 rounded-lg p-4">
                  <div className="text-2xl font-bold text-white">{behaviorMetrics.keyboardEvents}</div>
                  <div className="text-white/70 text-sm">Key Presses</div>
                </div>
                <div className="bg-white/10 rounded-lg p-4">
                  <div className="text-2xl font-bold text-white">{Math.floor(behaviorMetrics.timeSpent / 1000)}</div>
                  <div className="text-white/70 text-sm">Seconds</div>
                </div>
                <div className="bg-white/10 rounded-lg p-4">
                  <div className="text-2xl font-bold text-white">{behaviorMetrics.scrollBehavior}</div>
                  <div className="text-white/70 text-sm">Scrolls</div>
                </div>
              </div>
            </div>

            <div className="mt-12">
              <p className="text-white/70 text-lg">
                🔒 Protected by advanced bot detection • 
                🌐 Humans continue to main site • 
                🛡️ Powered by AI security
              </p>
            </div>
          </div>
        </div>
      </div>
    </BotProtection>
  );
};

export default App;