import { useEffect, useState, useRef } from 'react';

// Type definitions
interface BehaviorMetrics {
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

interface DetectionResult {
  isBot: boolean;
  confidence: number;
  detectionMethods: string[];
  fingerprint: string;
  riskLevel: string;
}

// Extended Window interface for browser APIs
declare global {
  interface Window {
    chrome?: {
      runtime?: unknown;
    };
    webkitAudioContext?: typeof AudioContext;
    callPhantom?: unknown;
    _phantom?: unknown;
    Buffer?: unknown;
  }
  
  interface Navigator {
    deviceMemory?: number;
    getBattery?: () => Promise<{
      level: number;
      charging: boolean;
    }>;
    connection?: {
      effectiveType?: string;
      downlink?: number;
    };
  }

  interface Performance {
    memory?: {
      usedJSHeapSize: number;
      totalJSHeapSize: number;
    };
  }
}

// Ultra-Advanced Bot Detection Hook
const useUltraBotDetection = () => {
  const [detectionResult, setDetectionResult] = useState<DetectionResult>({
    isBot: false,
    confidence: 0,
    detectionMethods: [],
    fingerprint: '',
    riskLevel: 'low'
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

  const startTimeRef = useRef(Date.now());
  const detectionIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Advanced Fingerprinting with 20+ vectors
  const generateUltraFingerprint = async (): Promise<string> => {
    const components: string[] = [];
    
    try {
      // Screen and Display Metrics (Multiple vectors)
      components.push(`screen:${screen.width}x${screen.height}x${screen.colorDepth}`);
      components.push(`avail:${screen.availWidth}x${screen.availHeight}`);
      components.push(`pixel:${window.devicePixelRatio || 1}`);
      components.push(`orientation:${(screen.orientation as any)?.angle || 0}`);
      
      // Timezone and Locale (High entropy)
      const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      components.push(`tz:${timeZone}`);
      components.push(`tzOffset:${new Date().getTimezoneOffset()}`);
      components.push(`lang:${navigator.language}`);
      components.push(`langs:${navigator.languages?.join(',') || 'none'}`);
      
      // Hardware Fingerprinting
      components.push(`cores:${navigator.hardwareConcurrency || 0}`);
      components.push(`memory:${navigator.deviceMemory || 0}`);
      components.push(`platform:${navigator.platform}`);
      components.push(`maxTouchPoints:${navigator.maxTouchPoints || 0}`);
      
      // Battery API (if available)
      try {
        if ('getBattery' in navigator && navigator.getBattery) {
          const battery = await navigator.getBattery();
          const batteryInfo = `${Math.round(battery.level * 100)}-${battery.charging}`;
          components.push(`battery:${batteryInfo}`);
          setBehaviorMetrics(prev => ({ ...prev, batteryLevel: battery.level }));
        }
      } catch (e) {
        components.push('battery:unavailable');
      }
      
      // Network Information
      if ('connection' in navigator && navigator.connection) {
        const conn = navigator.connection;
        components.push(`conn:${conn.effectiveType || 'unknown'}-${conn.downlink || 0}`);
        setBehaviorMetrics(prev => ({ ...prev, connectionType: conn.effectiveType || null }));
      }
      
      // Advanced Canvas Fingerprinting
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      if (ctx) {
        // Multiple canvas techniques
        ctx.textBaseline = 'alphabetic';
        ctx.fillStyle = '#f60';
        ctx.fillRect(125, 1, 62, 20);
        ctx.fillStyle = '#069';
        ctx.font = '11pt no-real-font-123';
        ctx.fillText('Ultra Bot Detection 2024 🤖👁️‍🗨️', 2, 15);
        ctx.fillStyle = 'rgba(102, 204, 0, 0.2)';
        ctx.font = '18pt Arial';
        ctx.fillText('Advanced Fingerprinting', 4, 45);
        
        // Add geometric shapes for more entropy
        ctx.beginPath();
        ctx.arc(50, 50, 20, 0, Math.PI * 2);
        ctx.strokeStyle = '#FF6B6B';
        ctx.stroke();
        
        // Add gradients
        const gradient = ctx.createLinearGradient(0, 0, 200, 0);
        gradient.addColorStop(0, 'red');
        gradient.addColorStop(1, 'blue');
        ctx.fillStyle = gradient;
        ctx.fillRect(10, 80, 100, 20);
        
        const canvasData = canvas.toDataURL();
        const canvasHash = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canvasData));
        const canvasFingerprint = Array.from(new Uint8Array(canvasHash))
          .map(b => b.toString(16).padStart(2, '0'))
          .join('')
          .substring(0, 16);
        components.push(`canvas:${canvasFingerprint}`);
        setBehaviorMetrics(prev => ({ ...prev, canvasFingerprint }));
      }
      
      // Advanced WebGL Fingerprinting
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
      if (gl && 'getParameter' in gl) {
        const webglCtx = gl as WebGLRenderingContext;
        const renderer = webglCtx.getParameter(webglCtx.RENDERER) || 'unknown';
        const vendor = webglCtx.getParameter(webglCtx.VENDOR) || 'unknown';
        const version = webglCtx.getParameter(webglCtx.VERSION) || 'unknown';
        
        // Get extensions
        const extensions = webglCtx.getSupportedExtensions() || [];
        const extCount = extensions.length;
        
        // Get WebGL parameters
        const maxTextureSize = webglCtx.getParameter(webglCtx.MAX_TEXTURE_SIZE);
        
        const webglInfo = `${vendor}-${renderer}-${version}-${extCount}-${maxTextureSize}`;
        const webglHash = btoa(webglInfo).substring(0, 16);
        components.push(`webgl:${webglHash}`);
        setBehaviorMetrics(prev => ({ ...prev, webglFingerprint: webglHash }));
      }
      
      // Audio Context Fingerprinting
      try {
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        if (AudioContextClass) {
          const audioContext = new AudioContextClass();
          const oscillator = audioContext.createOscillator();
          const analyser = audioContext.createAnalyser();
          const gain = audioContext.createGain();
          
          gain.gain.value = 0; // Mute
          oscillator.frequency.value = 1000;
          oscillator.connect(analyser);
          analyser.connect(gain);
          gain.connect(audioContext.destination);
          
          oscillator.start(0);
          oscillator.stop(0.1);
          
          const audioFingerprint = `${audioContext.sampleRate}-${analyser.fftSize}-${analyser.frequencyBinCount}`;
          components.push(`audio:${btoa(audioFingerprint).substring(0, 12)}`);
          setBehaviorMetrics(prev => ({ ...prev, audioFingerprint: btoa(audioFingerprint).substring(0, 12) }));
          
          audioContext.close();
        }
      } catch (e) {
        components.push('audio:unavailable');
      }
      
      // Font Detection (Comprehensive)
      const baseFonts = ['serif', 'sans-serif', 'monospace'];
      const testFonts = [
        'Arial', 'Arial Black', 'Arial Narrow', 'Arial Rounded MT Bold',
        'Helvetica', 'Helvetica Neue', 'Times', 'Times New Roman',
        'Courier', 'Courier New', 'Verdana', 'Georgia', 'Palatino',
        'Garamond', 'Bookman', 'Comic Sans MS', 'Trebuchet MS',
        'Impact', 'Lucida Console', 'Tahoma', 'Geneva', 'Lucida Grande',
        'Lucida Sans Unicode', 'MS Sans Serif', 'MS Serif'
      ];
      
      const detectedFonts = testFonts.filter(font => {
        return baseFonts.some(baseFont => detectFont(font, baseFont));
      });
      
      components.push(`fonts:${detectedFonts.length}-${detectedFonts.slice(0, 5).join(',')}`);
      
      // Plugin Enumeration
      const plugins = Array.from(navigator.plugins || []).map(p => p.name);
      components.push(`plugins:${plugins.length}-${plugins.slice(0, 3).join(',')}`);
      
      // Advanced Browser Features
      const features = [
        'serviceWorker' in navigator,
        'geolocation' in navigator,
        'webkitRequestFileSystem' in window,
        'webkitResolveLocalFileSystemURL' in window,
        'permissions' in navigator,
        'storage' in navigator,
        'bluetooth' in navigator,
        'usb' in navigator
      ];
      components.push(`features:${features.filter(Boolean).length}`);
      
      // Media Devices
      if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
        try {
          const devices = await navigator.mediaDevices.enumerateDevices();
          const deviceTypes = devices.map(d => d.kind);
          const audioInputs = deviceTypes.filter(t => t === 'audioinput').length;
          const videoInputs = deviceTypes.filter(t => t === 'videoinput').length;
          const audioOutputs = deviceTypes.filter(t => t === 'audiooutput').length;
          components.push(`media:${audioInputs}-${videoInputs}-${audioOutputs}`);
        } catch (e) {
          components.push('media:restricted');
        }
      }
      
      // Performance API
      if (window.performance && window.performance.memory) {
        const memory = window.performance.memory;
        const memInfo = `${Math.round(memory.usedJSHeapSize / 1048576)}-${Math.round(memory.totalJSHeapSize / 1048576)}`;
        components.push(`memory:${memInfo}`);
      }
      
      // Trusted Web Activity detection
      if (document.referrer && document.referrer.includes('android-app://')) {
        components.push('twa:true');
      }
      
      // PWA detection
      if (window.matchMedia('(display-mode: standalone)').matches) {
        components.push('pwa:standalone');
      }
      
    } catch (error) {
      const err = error as Error;
      components.push(`error:${err.message.substring(0, 20)}`);
    }
    
    // Generate final fingerprint with timestamp
    const timestamp = Math.floor(Date.now() / 300000); // 5-minute windows
    const fullFingerprint = components.join('|') + `|t:${timestamp}`;
    
    return btoa(fullFingerprint).substring(0, 64);
  };

  const detectFont = (font: string, baseFont: string): boolean => {
    const testString = "mmmmmmmmmmlli";
    const testSize = '72px';
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    
    if (!context) return false;
    
    context.font = testSize + ' ' + baseFont;
    const baseWidth = context.measureText(testString).width;
    
    context.font = testSize + ' ' + font + ', ' + baseFont;
    const newWidth = context.measureText(testString).width;
    
    return newWidth !== baseWidth;
  };

  // Ultra-Advanced User Agent Analysis
  const analyzeUserAgentUltra = (ua: string) => {
    if (!ua) return { isBot: true, confidence: 0.9, reasons: ['missing_user_agent'] };
    
    const reasons: string[] = [];
    let confidence = 0;
    
    // Comprehensive bot patterns with weighted scoring
    const ultraBotPatterns = [
      // Social Media Crawlers (Highest Priority)
      { pattern: /facebook|facebookexternalhit|facebot|facebookcatalog/i, weight: 0.98, type: 'social_crawler' },
      { pattern: /twitter|twitterbot|tweetmeme|tweetdeck/i, weight: 0.96, type: 'social_crawler' },
      { pattern: /linkedin|linkedinbot/i, weight: 0.95, type: 'social_crawler' },
      { pattern: /instagram|instagrambot/i, weight: 0.94, type: 'social_crawler' },
      { pattern: /pinterest|pinterestbot/i, weight: 0.93, type: 'social_crawler' },
      { pattern: /whatsapp|whatsappbot/i, weight: 0.92, type: 'social_crawler' },
      
      // Search Engine Bots
      { pattern: /google|googlebot|googleother|adsbot-google|mediapartners-google/i, weight: 0.90, type: 'search_engine' },
      { pattern: /bing|bingbot|msnbot|bingpreview/i, weight: 0.88, type: 'search_engine' },
      { pattern: /yahoo|slurp|yahooseeker/i, weight: 0.87, type: 'search_engine' },
      { pattern: /baidu|baiduspider|baiduboxapp/i, weight: 0.86, type: 'search_engine' },
      { pattern: /yandex|yandexbot|yandexmobilebot/i, weight: 0.85, type: 'search_engine' },
      { pattern: /duckduckgo|duckduckbot/i, weight: 0.84, type: 'search_engine' },
      
      // Automation Tools (Critical Detection)
      { pattern: /selenium|webdriver/i, weight: 0.99, type: 'automation' },
      { pattern: /puppeteer|playwright/i, weight: 0.98, type: 'automation' },
      { pattern: /phantomjs|phantom|slimerjs/i, weight: 0.97, type: 'automation' },
      { pattern: /headless|chrome-headless/i, weight: 0.96, type: 'automation' },
      { pattern: /jsdom|zombie/i, weight: 0.95, type: 'automation' },
      
      // Script Tools
      { pattern: /curl|wget|httpie|postman/i, weight: 0.94, type: 'script_tool' },
      { pattern: /python-requests|python-urllib|requests-html/i, weight: 0.93, type: 'script_tool' },
      { pattern: /axios|node-fetch|got|superagent/i, weight: 0.91, type: 'script_tool' },
      { pattern: /ruby|mechanize|httparty|faraday/i, weight: 0.90, type: 'script_tool' },
      { pattern: /java|apache-httpclient|okhttp|unirest/i, weight: 0.89, type: 'script_tool' },
      { pattern: /go-http-client|golang/i, weight: 0.88, type: 'script_tool' },
      { pattern: /php|guzzle|cURL/i, weight: 0.87, type: 'script_tool' },
      
      // Monitoring and Testing
      { pattern: /monitor|uptime|pingdom|newrelic/i, weight: 0.85, type: 'monitoring' },
      { pattern: /test|check|probe|scan|audit/i, weight: 0.80, type: 'testing' },
      { pattern: /lighthouse|pagespeed|gtmetrix/i, weight: 0.82, type: 'performance' },
      
      // Generic Bot Patterns
      { pattern: /\bbot\b|crawler|spider|scraper|harvester/i, weight: 0.75, type: 'generic_bot' },
      { pattern: /feed|rss|atom|sitemap/i, weight: 0.70, type: 'content_bot' },
      { pattern: /link.?check|validator|archiver/i, weight: 0.68, type: 'utility_bot' },
      
      // Suspicious Patterns
      { pattern: /^mozilla\/[45]\.0.*rv:[0-9]+.*gecko\/[0-9]+.*firefox\/[0-9]+.*$/i, weight: 0.60, type: 'suspicious_firefox' },
      { pattern: /^mozilla\/5\.0.*chrome\/[0-9]+.*safari\/[0-9]+.*$/i, weight: 0.55, type: 'suspicious_chrome' },
    ];
    
    // Pattern matching
    let maxWeight = 0;
    const detectedTypes: string[] = [];
    
    for (const botPattern of ultraBotPatterns) {
      if (botPattern.pattern.test(ua)) {
        reasons.push(`${botPattern.type}_detected`);
        detectedTypes.push(botPattern.type);
        maxWeight = Math.max(maxWeight, botPattern.weight);
      }
    }
    
    confidence = maxWeight;
    
    // Advanced heuristic analysis
    const uaLength = ua.length;
    
    // Length analysis
    if (uaLength < 10) {
      reasons.push('extremely_short_ua');
      confidence = Math.max(confidence, 0.85);
    } else if (uaLength < 30) {
      reasons.push('very_short_ua');
      confidence = Math.max(confidence, 0.70);
    } else if (uaLength > 2000) {
      reasons.push('extremely_long_ua');
      confidence = Math.max(confidence, 0.75);
    }
    
    // Browser version analysis
    const chromeMatch = ua.match(/Chrome\/(\d+)\.(\d+)\.(\d+)\.(\d+)/);
    if (chromeMatch) {
      const major = parseInt(chromeMatch[1]);
      const minor = parseInt(chromeMatch[2]);
      const build = parseInt(chromeMatch[3]);
      const patch = parseInt(chromeMatch[4]);
      
      // Unrealistic version numbers
      if (major < 60 || major > 200) {
        reasons.push('suspicious_chrome_major_version');
        confidence = Math.max(confidence, 0.60);
      }
      
      // Perfect version patterns (often synthetic)
      if (minor === 0 && build === 0 && patch === 0) {
        reasons.push('perfect_chrome_version_pattern');
        confidence = Math.max(confidence, 0.45);
      }
    }
    
    // Firefox analysis
    const firefoxMatch = ua.match(/Firefox\/(\d+)\.(\d+)/);
    if (firefoxMatch) {
      const major = parseInt(firefoxMatch[1]);
      if (major < 70 || major > 200) {
        reasons.push('suspicious_firefox_version');
        confidence = Math.max(confidence, 0.60);
      }
    }
    
    // OS inconsistency checks
    const hasWindows = /Windows/i.test(ua);
    const hasMac = /Mac OS X|Macintosh/i.test(ua);
    const hasLinux = /Linux/i.test(ua);
    const hasAndroid = /Android/i.test(ua);
    const hasiOS = /iPhone|iPad|iPod/i.test(ua);
    
    const osCount = [hasWindows, hasMac, hasLinux, hasAndroid, hasiOS].filter(Boolean).length;
    
    if (osCount > 1) {
      reasons.push('multiple_os_identifiers');
      confidence = Math.max(confidence, 0.70);
    } else if (osCount === 0) {
      reasons.push('no_os_identifier');
      confidence = Math.max(confidence, 0.65);
    }
    
    // Browser feature inconsistencies
    const hasChrome = /Chrome/i.test(ua);
    const hasSafari = /Safari/i.test(ua);
    const hasFirefox = /Firefox/i.test(ua);
    const hasEdge = /Edge|Edg\//i.test(ua);
    
    const browserCount = [hasChrome, hasSafari, hasFirefox, hasEdge].filter(Boolean).length;
    
    if (browserCount === 0) {
      reasons.push('no_browser_identifier');
      confidence = Math.max(confidence, 0.80);
    } else if (browserCount > 2) {
      reasons.push('too_many_browser_identifiers');
      confidence = Math.max(confidence, 0.60);
    }
    
    // Entropy analysis
    const entropy = calculateStringEntropy(ua);
    if (entropy < 3.0) {
      reasons.push('low_entropy_user_agent');
      confidence = Math.max(confidence, 0.40);
    }
    
    // Unusual character patterns
    if (/[^\x20-\x7E]/.test(ua)) {
      reasons.push('non_ascii_characters');
      confidence = Math.max(confidence, 0.50);
    }
    
    // Sequential number patterns (often synthetic)
    if (/\d{5,}/.test(ua) || /(\d\.){3,}/.test(ua)) {
      reasons.push('suspicious_number_patterns');
      confidence = Math.max(confidence, 0.35);
    }
    
    return { 
      isBot: confidence > 0.6, 
      confidence, 
      reasons,
      detectedTypes
    };
  };

  const calculateStringEntropy = (str: string): number => {
    if (!str) return 0;
    
    const charCount: Record<string, number> = {};
    for (const char of str) {
      charCount[char] = (charCount[char] || 0) + 1;
    }
    
    let entropy = 0;
    const length = str.length;
    
    for (const count of Object.values(charCount)) {
      const probability = count / length;
      entropy -= probability * Math.log2(probability);
    }
    
    return entropy;
  };

  // Ultra-Advanced Behavioral Analysis
  const analyzeUltraBehavior = () => {
    const reasons: string[] = [];
    let confidence = 0;
    
    const timeSpent = behaviorMetrics.timeSpent;
    const interactions = behaviorMetrics.mouseMovements + behaviorMetrics.keyboardEvents + behaviorMetrics.scrollBehavior;
    
    // Zero interaction analysis (weighted by time)
    if (timeSpent > 3000 && interactions === 0) {
      reasons.push('zero_interactions_extended_time');
      confidence += 0.70;
    } else if (timeSpent > 1000 && behaviorMetrics.mouseMovements === 0) {
      reasons.push('no_mouse_movement');
      confidence += 0.50;
    }
    
    // Interaction timing analysis
    if (behaviorMetrics.clickPatterns.length > 2) {
      const avgInterval = behaviorMetrics.clickPatterns.reduce((a, b) => a + b, 0) / behaviorMetrics.clickPatterns.length;
      const variance = behaviorMetrics.clickPatterns.reduce((sum, interval) => {
        return sum + Math.pow(interval - avgInterval, 2);
      }, 0) / behaviorMetrics.clickPatterns.length;
      
      // Impossibly fast
      if (avgInterval < 30) {
        reasons.push('superhuman_click_speed');
        confidence += 0.80;
      }
      // Too regular (robotic)
      else if (variance < 100 && avgInterval < 200) {
        reasons.push('robotic_click_timing');
        confidence += 0.60;
      }
    }
    
    // Mouse velocity analysis
    if (behaviorMetrics.mouseVelocity.length > 10) {
      const avgVelocity = behaviorMetrics.mouseVelocity.reduce((a, b) => a + b, 0) / behaviorMetrics.mouseVelocity.length;
      const maxVelocity = Math.max(...behaviorMetrics.mouseVelocity);
      
      if (maxVelocity > 5000) {
        reasons.push('impossible_mouse_velocity');
        confidence += 0.75;
      } else if (avgVelocity > 0 && avgVelocity < 2) {
        reasons.push('impossibly_slow_mouse');
        confidence += 0.65;
      }
    }
    
    // Device motion analysis
    if (timeSpent > 10000 && !behaviorMetrics.deviceMotion && !behaviorMetrics.orientationChange) {
      reasons.push('no_device_physics');
      confidence += 0.40;
    }
    
    // Screen interaction patterns
    if (behaviorMetrics.mouseMovements > 100 && behaviorMetrics.mouseEntropy < 2.0) {
      reasons.push('low_mouse_entropy');
      confidence += 0.45;
    }
    
    return { confidence: Math.min(confidence, 1.0), reasons };
  };

  // Environment Analysis for Headless/Automated Browsers
  const analyzeEnvironment = () => {
    const reasons: string[] = [];
    let confidence = 0;
    
    // Direct bot indicators
    if (window.navigator.webdriver) {
      reasons.push('webdriver_property');
      confidence += 0.95;
    }
    
    if (window.callPhantom || window._phantom) {
      reasons.push('phantom_detected');
      confidence += 0.90;
    }
    
    if (window.Buffer) {
      reasons.push('nodejs_buffer_detected');
      confidence += 0.85;
    }
    
    // Missing browser objects
    if (!window.chrome && navigator.userAgent.includes('Chrome')) {
      reasons.push('missing_chrome_object');
      confidence += 0.60;
    }
    
    // Viewport analysis
    if (window.outerHeight === 0 || window.outerWidth === 0) {
      reasons.push('zero_outer_dimensions');
      confidence += 0.70;
    }
    
    // Plugin analysis
    if (navigator.plugins.length === 0 && !navigator.userAgent.includes('Mobile')) {
      reasons.push('no_plugins');
      confidence += 0.50;
    }
    
    // Language checks
    if (!navigator.languages || navigator.languages.length === 0) {
      reasons.push('no_languages');
      confidence += 0.60;
    }
    
    // Permissions API inconsistencies
    if (navigator.permissions) {
      try {
        navigator.permissions.query({ name: 'notifications' }).catch(() => {
          reasons.push('permissions_api_error');
          confidence += 0.30;
        });
      } catch (e) {
        reasons.push('permissions_api_unavailable');
        confidence += 0.40;
      }
    }
    
    return { confidence: Math.min(confidence, 1.0), reasons };
  };

  // Main Detection Function
  const runUltraDetection = async (): Promise<DetectionResult> => {
    const fingerprint = await generateUltraFingerprint();
    const userAgent = navigator.userAgent;
    
    // Run all analysis layers
    const uaAnalysis = analyzeUserAgentUltra(userAgent);
    const behaviorAnalysis = analyzeUltraBehavior();
    const environmentAnalysis = analyzeEnvironment();
    
    // Weighted confidence calculation
    const confidenceScores = [
      { score: uaAnalysis.confidence, weight: 0.4 },
      { score: behaviorAnalysis.confidence, weight: 0.35 },
      { score: environmentAnalysis.confidence, weight: 0.25 }
    ];
    
    const weightedConfidence = confidenceScores.reduce((sum, item) => {
      return sum + (item.score * item.weight);
    }, 0);
    
    // Combine all detection methods
    const allMethods = [
      ...uaAnalysis.reasons,
      ...behaviorAnalysis.reasons,
      ...environmentAnalysis.reasons
    ];
    
    // Risk level calculation
    let riskLevel = 'low';
    if (weightedConfidence >= 0.8) riskLevel = 'critical';
    else if (weightedConfidence >= 0.6) riskLevel = 'high';
    else if (weightedConfidence >= 0.4) riskLevel = 'medium';
    
    const result: DetectionResult = {
      isBot: weightedConfidence >= 0.6,
      confidence: weightedConfidence,
      detectionMethods: allMethods,
      fingerprint,
      riskLevel
    };
    
    setDetectionResult(result);
    return result;
  };

  // Enhanced Behavior Tracking
  useEffect(() => {
    let mousePositions: Array<{x: number, y: number, time: number}> = [];
    let velocities: number[] = [];
    let accelerations: number[] = [];
    let lastPosition = { x: 0, y: 0, time: 0 };
    let lastVelocity = { x: 0, y: 0, time: 0 };
    
    const handleMouseMove = (e: MouseEvent) => {
      const now = Date.now();
      const position = { x: e.clientX, y: e.clientY, time: now };
      
      mousePositions.push(position);
      if (mousePositions.length > 1000) mousePositions.shift();
      
      // Calculate velocity
      if (lastPosition.time > 0) {
        const timeDiff = (now - lastPosition.time) / 1000;
        if (timeDiff > 0) {
          const velocityX = (position.x - lastPosition.x) / timeDiff;
          const velocityY = (position.y - lastPosition.y) / timeDiff;
          const speed = Math.sqrt(velocityX * velocityX + velocityY * velocityY);
          
          velocities.push(speed);
          if (velocities.length > 200) velocities.shift();
          
          // Calculate acceleration
          if (lastVelocity.time > 0) {
            const accelTimeDiff = (now - lastVelocity.time) / 1000;
            if (accelTimeDiff > 0) {
              const accelX = (velocityX - lastVelocity.x) / accelTimeDiff;
              const accelY = (velocityY - lastVelocity.y) / accelTimeDiff;
              const acceleration = Math.sqrt(accelX * accelX + accelY * accelY);
              
              accelerations.push(acceleration);
              if (accelerations.length > 100) accelerations.shift();
            }
          }
          
          lastVelocity = { x: velocityX, y: velocityY, time: now };
        }
      }
      
      lastPosition = position;
      
      setBehaviorMetrics(prev => ({
        ...prev,
        mouseMovements: prev.mouseMovements + 1,
        mouseVelocity: [...velocities],
        mouseAcceleration: [...accelerations]
      }));
      
      // Calculate entropy from recent positions
      if (mousePositions.length >= 50) {
        const entropy = calculateMouseEntropy(mousePositions.slice(-50));
        setBehaviorMetrics(prev => ({ ...prev, mouseEntropy: entropy }));
      }
    };

    const calculateMouseEntropy = (positions: Array<{x: number, y: number, time: number}>): number => {
      const gridSize = 25;
      const grid: Record<string, number> = {};
      
      positions.forEach(pos => {
        const gridX = Math.floor(pos.x / gridSize);
        const gridY = Math.floor(pos.y / gridSize);
        const key = `${gridX},${gridY}`;
        grid[key] = (grid[key] || 0) + 1;
      });
      
      const total = positions.length;
      let entropy = 0;
      
      Object.values(grid).forEach(count => {
        const probability = count / total;
        entropy -= probability * Math.log2(probability);
      });
      
      return entropy;
    };

    const handleClick = () => {
      const now = Date.now();
      setBehaviorMetrics(prev => {
        const newClickTiming = [...prev.clickTiming, now];
        if (newClickTiming.length > 1) {
          const intervals: number[] = [];
          for (let i = 1; i < newClickTiming.length; i++) {
            intervals.push(newClickTiming[i] - newClickTiming[i - 1]);
          }
          return {
            ...prev,
            clickTiming: newClickTiming.slice(-20),
            clickPatterns: intervals.slice(-15)
          };
        }
        return { ...prev, clickTiming: newClickTiming };
      });
    };

    const handleKeyboard = () => {
      setBehaviorMetrics(prev => ({
        ...prev,
        keyboardEvents: prev.keyboardEvents + 1
      }));
    };

    const handleScroll = (e: Event) => {
      const wheelEvent = e as WheelEvent;
      setBehaviorMetrics(prev => ({
        ...prev,
        scrollBehavior: prev.scrollBehavior + 1,
        scrollDelta: [...prev.scrollDelta.slice(-19), wheelEvent.deltaY || 0]
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

    const updateTimeSpent = () => {
      const timeSpent = Date.now() - startTimeRef.current;
      setBehaviorMetrics(prev => ({ ...prev, timeSpent }));
    };

    // Add event listeners
    document.addEventListener('mousemove', handleMouseMove, { passive: true });
    document.addEventListener('click', handleClick);
    document.addEventListener('keydown', handleKeyboard);
    document.addEventListener('scroll', handleScroll, { passive: true });
    document.addEventListener('touchstart', handleTouch, { passive: true });
    document.addEventListener('focus', handleFocus);
    window.addEventListener('devicemotion', handleDeviceMotion);
    window.addEventListener('orientationchange', handleOrientationChange);

    const timeInterval = setInterval(updateTimeSpent, 500);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('click', handleClick);
      document.removeEventListener('keydown', handleKeyboard);
      document.removeEventListener('scroll', handleScroll);
      document.removeEventListener('touchstart', handleTouch);
      document.removeEventListener('focus', handleFocus);
      window.removeEventListener('devicemotion', handleDeviceMotion);
      window.removeEventListener('orientationchange', handleOrientationChange);
      clearInterval(timeInterval);
    };
  }, []);

  // Server Communication
  const checkWithServer = async (): Promise<any> => {
    try {
      const response = await fetch('http://localhost:8000/api/bot-detection/detect/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_agent: navigator.userAgent,
          fingerprint: detectionResult.fingerprint,
          is_bot: detectionResult.isBot,
          confidence: detectionResult.confidence,
          methods: detectionResult.detectionMethods,
          behavioral: behaviorMetrics,
          timestamp: new Date().toISOString(),
          page: window.location.href,
          referrer: document.referrer,
          url_path: window.location.pathname,
          http_method: 'GET',
          risk_level: detectionResult.riskLevel
        })
      });

      if (response.ok) {
        const serverResult = await response.json();
        return serverResult;
      }
    } catch (error) {
      const err = error as Error;
      console.warn('Server detection unavailable:', err.message);
    }
    return null;
  };

  // Detection Loop
  useEffect(() => {
    // Initial detection after minimal interaction time
    const initialDetection = setTimeout(async () => {
      await runUltraDetection();
    }, 1000);

    // Periodic re-detection
    detectionIntervalRef.current = setInterval(async () => {
      const result = await runUltraDetection();
      
      // Check with server if confidence is medium-high
      if (result.confidence > 0.4) {
        const serverResult = await checkWithServer();
        if (serverResult && serverResult.blocked) {
          setDetectionResult(prev => ({
            ...prev,
            isBot: true,
            confidence: Math.max(prev.confidence, serverResult.confidence || 0.8),
            detectionMethods: [...prev.detectionMethods, 'server_confirmation']
          }));
        }
      }
    }, 3000);

    return () => {
      clearTimeout(initialDetection);
      if (detectionIntervalRef.current) {
        clearInterval(detectionIntervalRef.current);
      }
    };
  }, []);

  return {
    detectionResult,
    behaviorMetrics,
    runUltraDetection,
    checkWithServer
  };
};

// Minimal Loading Spinner (Clean & Fast)
const MinimalLoader = () => (
  <div className="fixed inset-0 bg-gradient-to-br from-indigo-600 via-purple-600 to-blue-700 flex items-center justify-center">
    <div className="text-center">
      {/* Animated Spinner */}
      <div className="relative mb-8">
        <div className="w-12 h-12 border-3 border-white/20 rounded-full animate-spin border-t-white"></div>
        <div 
          className="absolute inset-0 w-12 h-12 border-3 border-transparent border-t-blue-200 rounded-full animate-spin" 
          style={{ animationDelay: '0.15s', animationDuration: '1.2s' }}
        ></div>
      </div>
      
      {/* Minimal Text */}
      <div className="text-white/90 text-lg font-medium">
        Loading...
      </div>
    </div>
  </div>
);

// Bot Content (Only shown to detected bots)
const BotContent: React.FC<{ detectionResult: DetectionResult; behaviorMetrics: BehaviorMetrics }> = ({ 
  detectionResult, 
  behaviorMetrics 
}) => (
  <div className="min-h-screen bg-gradient-to-br from-slate-800 via-purple-800 to-indigo-900">
    <div className="container mx-auto px-4 py-8">
      <div className="text-center">
        <div className="mb-8">
          <div className="inline-flex items-center justify-center w-24 h-24 bg-white/10 backdrop-blur-lg rounded-full mb-6 border border-white/20">
            <span className="text-4xl">🤖</span>
          </div>
          
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-4">
            Dogify Bot Portal
          </h1>
          
          <p className="text-lg text-white/80 mb-6 max-w-2xl mx-auto">
            Automated access detected. This is the designated bot interface.
          </p>
        </div>
        
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 max-w-lg mx-auto border border-white/20">
          <h3 className="text-white font-bold text-lg mb-4">Detection Summary</h3>
          <div className="space-y-2 text-white/90">
            <div className="flex justify-between">
              <span>Confidence:</span>
              <span className="font-mono">{Math.round(detectionResult.confidence * 100)}%</span>
            </div>
            <div className="flex justify-between">
              <span>Risk Level:</span>
              <span className="font-mono capitalize">{detectionResult.riskLevel}</span>
            </div>
            <div className="flex justify-between">
              <span>Methods:</span>
              <span className="font-mono">{detectionResult.detectionMethods.length}</span>
            </div>
            <div className="flex justify-between">
              <span>Session Time:</span>
              <span className="font-mono">{Math.floor(behaviorMetrics.timeSpent / 1000)}s</span>
            </div>
          </div>
        </div>

        <div className="mt-8 text-white/60 text-sm">
          🔒 Advanced Multi-Layer Bot Detection System
        </div>
      </div>
    </div>
  </div>
);

// Main App Component
const App = () => {
  const [redirecting, setRedirecting] = useState(false);
  const [showBot, setShowBot] = useState(false);
  const { detectionResult, behaviorMetrics } = useUltraBotDetection();

  useEffect(() => {
    const checkDetectionResult = () => {
      if (detectionResult.confidence > 0) {
        if (detectionResult.isBot && detectionResult.confidence >= 0.6) {
          // High confidence bot - show bot content
          setShowBot(true);
          return;
        }
        
        // Human detection logic
        if (detectionResult.confidence < 0.3 && behaviorMetrics.timeSpent > 2000) {
          // Low bot confidence + some interaction time = likely human
          if (!redirecting && !showBot) {
            setRedirecting(true);
            // Fast redirect for humans
            setTimeout(() => {
              window.location.href = "http://localhost:5173";
            }, 800);
          }
        }
        
        // Additional human indicators
        const humanIndicators = (
          behaviorMetrics.mouseMovements > 5 ||
          behaviorMetrics.keyboardEvents > 0 ||
          behaviorMetrics.scrollBehavior > 0 ||
          behaviorMetrics.touchEvents > 0
        );
        
        if (humanIndicators && detectionResult.confidence < 0.5 && behaviorMetrics.timeSpent > 3000) {
          if (!redirecting && !showBot) {
            setRedirecting(true);
            setTimeout(() => {
              window.location.href = "http://localhost:5173";
            }, 600);
          }
        }
      }
    };

    checkDetectionResult();
  }, [detectionResult, behaviorMetrics, redirecting, showBot]);

  // Show bot content for detected bots
  if (showBot) {
    return <BotContent detectionResult={detectionResult} behaviorMetrics={behaviorMetrics} />;
  }

  // Show minimal loader for humans (while detecting and before redirect)
  return <MinimalLoader />;
};

export default App;