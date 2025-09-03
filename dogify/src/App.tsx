import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { CartProvider } from './contexts/CartContext';
import { WishlistProvider } from './contexts/WishlistContext';

import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';
import Shop from './pages/Shop';
import ProductDetail from './pages/ProductDetail';
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';
import About from './pages/About';
import Contact from './pages/Contact';

// Import the enhanced bot detection hook with backend integration
import useEnhancedBotDetectionWithBackend, { 
  type DetectionResult, 
  type BehaviorMetrics 
} from './hooks/useEnhancedBotDetectionWithBackend';

// Component prop interfaces
interface BotContentProps {
  detectionResult: DetectionResult;
  behaviorMetrics: BehaviorMetrics;
}

interface DogFoodWebsiteProps {
  detectionResult: DetectionResult;
  behaviorMetrics: BehaviorMetrics;
}

// Enhanced Loading Spinner with better UX
const EnhancedLoader: React.FC = () => (
  <div className="fixed inset-0 bg-gradient-to-br from-indigo-600 via-purple-600 to-blue-700 flex items-center justify-center">
    <div className="text-center">
      {/* Animated Spinner */}
      <div className="relative mb-8">
        <div className="w-16 h-16 border-4 border-white/20 rounded-full animate-spin border-t-white"></div>
        <div 
          className="absolute inset-0 w-16 h-16 border-4 border-transparent border-t-blue-200 rounded-full animate-spin" 
          style={{ animationDelay: '0.15s', animationDuration: '1.2s' }}
        ></div>
      </div>
      
      {/* Dynamic Loading Text */}
      <div className="text-white/90 text-lg font-medium mb-2">
        Analyzing visitor patterns...
      </div>
      <div className="text-white/70 text-sm">
        🔍 Advanced security check in progress
      </div>
    </div>
  </div>
);

// Enhanced Bot Content with better Facebook bot handling
const BotContent: React.FC<BotContentProps> = ({ detectionResult, behaviorMetrics }) => {
  const isFacebookBot = detectionResult.isFacebookBot || 
    detectionResult.detectionMethods.some((method: string) => 
      method.includes('facebook') || method.includes('facebot')
    );

  const backendBlocked = detectionResult.backendResult?.blocked || false;
  const showDogWebsite = detectionResult.showDogWebsite || isFacebookBot;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-800 via-purple-800 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="mb-8">
            <div className="inline-flex items-center justify-center w-32 h-32 bg-white/10 backdrop-blur-lg rounded-full mb-6 border border-white/20">
              <span className="text-5xl">
                {isFacebookBot ? '🤖📘' : backendBlocked ? '🚫' : '🤖'}
              </span>
            </div>
            
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-4">
              {isFacebookBot ? 'Welcome Facebook Bot!' : 'Access Analysis Complete'}
            </h1>
            
            {isFacebookBot && (
              <div className="bg-blue-600/20 backdrop-blur-lg rounded-xl p-6 mb-6 border border-blue-400/30">
                <h2 className="text-2xl font-bold text-blue-200 mb-2">Facebook Crawler Detected</h2>
                <p className="text-blue-100">
                  Hello Facebook! You're viewing the optimized version of Dogify - our premium dog food store.
                </p>
              </div>
            )}
            
            {backendBlocked && (
              <div className="bg-red-600/20 backdrop-blur-lg rounded-xl p-6 mb-6 border border-red-400/30">
                <h2 className="text-2xl font-bold text-red-200 mb-2">Access Restricted</h2>
                <p className="text-red-100">
                  Automated access detected. Please visit our main site for the full experience.
                </p>
              </div>
            )}
            
            <p className="text-lg text-white/80 mb-6 max-w-2xl mx-auto">
              Premium nutrition for your furry friends. {isFacebookBot ? 'Showing SEO-optimized content.' : 'Advanced bot detection active.'}
            </p>
          </div>
          
          {/* Enhanced Dog Food Products Display */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 hover:bg-white/15 transition-colors">
              <div className="text-5xl mb-4">🥘</div>
              <h3 className="text-xl font-bold text-white mb-2">Premium Grain-Free Adult Dog Food</h3>
              <p className="text-white/70 mb-3">High-quality grain-free nutrition with real chicken as the first ingredient</p>
              <div className="text-green-400 font-bold text-xl mb-2">$49.99</div>
              <div className="text-white/60 text-sm">⭐⭐⭐⭐⭐ (4.8/5) • 234 reviews</div>
            </div>
            
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 hover:bg-white/15 transition-colors">
              <div className="text-5xl mb-4">🦴</div>
              <h3 className="text-xl font-bold text-white mb-2">Puppy Training Treats</h3>
              <p className="text-white/70 mb-3">Small, soft training treats perfect for puppies and small dogs</p>
              <div className="text-green-400 font-bold text-xl mb-2">$12.99</div>
              <div className="text-white/60 text-sm">⭐⭐⭐⭐⭐ (4.9/5) • 156 reviews</div>
            </div>
            
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 hover:bg-white/15 transition-colors">
              <div className="text-5xl mb-4">🥫</div>
              <h3 className="text-xl font-bold text-white mb-2">Senior Dog Wellness Formula</h3>
              <p className="text-white/70 mb-3">Joint support and easy digestion for senior dogs</p>
              <div className="text-green-400 font-bold text-xl mb-2">$44.99</div>
              <div className="text-white/60 text-sm">⭐⭐⭐⭐⭐ (4.7/5) • 89 reviews</div>
            </div>
          </div>

          {/* Enhanced Detection Summary */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 max-w-2xl mx-auto border border-white/20 mb-6">
            <h3 className="text-white font-bold text-lg mb-4 flex items-center gap-2">
              🔍 Detection Summary
              {detectionResult.backendVerified && (
                <span className="text-xs bg-green-500/20 text-green-300 px-2 py-1 rounded-full">
                  Backend Verified
                </span>
              )}
            </h3>
            <div className="grid grid-cols-2 gap-4 text-white/90">
              <div className="text-left">
                <div className="flex justify-between mb-2">
                  <span>Confidence:</span>
                  <span className="font-mono text-green-300">
                    {Math.round(detectionResult.confidence * 100)}%
                  </span>
                </div>
                <div className="flex justify-between mb-2">
                  <span>Risk Level:</span>
                  <span className="font-mono capitalize text-yellow-300">
                    {detectionResult.riskLevel}
                  </span>
                </div>
                <div className="flex justify-between mb-2">
                  <span>Facebook Bot:</span>
                  <span className="font-mono text-blue-300">
                    {isFacebookBot ? 'Yes' : 'No'}
                  </span>
                </div>
              </div>
              <div className="text-left">
                <div className="flex justify-between mb-2">
                  <span>Methods:</span>
                  <span className="font-mono text-cyan-300">
                    {detectionResult.detectionMethods.length}
                  </span>
                </div>
                <div className="flex justify-between mb-2">
                  <span>Session Time:</span>
                  <span className="font-mono text-orange-300">
                    {Math.floor(behaviorMetrics.timeSpent / 1000)}s
                  </span>
                </div>
              </div>
            </div>
            
            {/* Show specific detection methods for transparency */}
            {detectionResult.detectionMethods.length > 0 && (
              <div className="mt-4 pt-4 border-t border-white/20">
                <div className="text-xs text-white/60 mb-2">Detection Methods:</div>
                <div className="flex flex-wrap gap-1">
                  {detectionResult.detectionMethods.slice(0, 5).map((method, index) => (
                    <span key={index} className="text-xs bg-white/10 text-white/80 px-2 py-1 rounded">
                      {method.replace(/_/g, ' ')}
                    </span>
                  ))}
                  {detectionResult.detectionMethods.length > 5 && (
                    <span className="text-xs text-white/60">
                      +{detectionResult.detectionMethods.length - 5} more
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Backend Status Indicator */}
          {detectionResult.backendResult && (
            <div className="mb-6">
              <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm ${
                detectionResult.backendResult.status === 'blocked' 
                  ? 'bg-red-500/20 text-red-300'
                  : 'bg-green-500/20 text-green-300'
              }`}>
                <div className={`w-2 h-2 rounded-full ${
                  detectionResult.backendResult.status === 'blocked' ? 'bg-red-400' : 'bg-green-400'
                } animate-pulse`}></div>
                Backend Status: {detectionResult.backendResult.status || 'Active'}
              </div>
            </div>
          )}

          <div className="text-white/60 text-sm">
            🔒 Advanced Multi-Layer Bot Detection System with Real-Time Backend Verification
          </div>
          
          {/* SEO-friendly content for crawlers */}
          <div className="mt-12 bg-white/5 rounded-xl p-8 max-w-4xl mx-auto text-left">
            <h2 className="text-2xl font-bold text-white mb-4">About Dogify - Premium Dog Food Store</h2>
            <div className="text-white/80 space-y-4">
              <p>
                Dogify is your trusted source for premium dog nutrition. We offer a wide variety of 
                high-quality dog food, treats, and supplements to keep your furry friends healthy and happy.
              </p>
              <p>
                Our products include grain-free dry food, nutritious wet food varieties, training treats, 
                dental chews, and specialized formulas for puppies, adult dogs, and seniors.
              </p>
              <p>
                <strong>Featured Products:</strong> Premium Grain-Free Adult Dog Food ($49.99), 
                Puppy Training Treats ($12.99), Senior Dog Wellness Formula ($44.99), 
                Organic Wet Food Variety Pack ($32.99), High-Protein Active Dog Formula ($54.99)
              </p>
              <p>
                We provide fast, reliable shipping and excellent customer service. 
                Free shipping on orders over $50. Contact us at support@dogify.com
              </p>
              <p>
                <strong>Store Hours:</strong> Monday-Friday 8AM-8PM CST, Saturday 9AM-6PM CST, Sunday 10AM-4PM CST
              </p>
              <p>
                <strong>Address:</strong> 123 Pet Paradise Lane, Austin, TX 78701, United States
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Enhanced Dog Food Website (shown to Facebook bots and medium-confidence bots)
const DogFoodWebsite: React.FC<DogFoodWebsiteProps> = ({ detectionResult }) => (
  <CartProvider>
    <WishlistProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Header />
          <main>
            {/* Add a banner for detected bots */}
            {detectionResult.isBot && (
              <div className="bg-blue-50 border-b border-blue-200 px-4 py-2">
                <div className="max-w-7xl mx-auto">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-blue-600">🤖</span>
                      <span className="text-sm text-blue-800">
                        Bot visitor detected - showing optimized content
                      </span>
                      {detectionResult.isFacebookBot && (
                        <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded">
                          Facebook Bot
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-blue-600">
                      Confidence: {Math.round(detectionResult.confidence * 100)}%
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/shop" element={<Shop />} />
              <Route path="/product/:id" element={<ProductDetail />} />
              <Route path="/cart" element={<Cart />} />
              <Route path="/checkout" element={<Checkout />} />
              <Route path="/about" element={<About />} />
              <Route path="/contact" element={<Contact />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </WishlistProvider>
  </CartProvider>
);

// Main App Component with Enhanced Logic
const App: React.FC = () => {
  const [redirecting, setRedirecting] = useState<boolean>(false);
  const [showBot, setShowBot] = useState<boolean>(false);
  const [showDogWebsite, setShowDogWebsite] = useState<boolean>(false);
  const [debugMode, setDebugMode] = useState<boolean>(false);
  const [analysisComplete, setAnalysisComplete] = useState<boolean>(false);
  
  const { detectionResult, behaviorMetrics } = useEnhancedBotDetectionWithBackend();

  // Enable debug mode with URL parameter
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    setDebugMode(urlParams.get('debug') === 'true');
  }, []);

  useEffect(() => {
    const checkDetectionResult = () => {
      if (detectionResult.confidence > 0 || detectionResult.backendVerified) {
        console.log('🔍 Enhanced detection result:', detectionResult);
        setAnalysisComplete(true);
        
        // Check if backend blocked the request
        if (detectionResult.backendResult?.blocked) {
          console.log('🚫 Backend blocked - showing bot content');
          setShowBot(true);
          return;
        }
        
        // Priority 1: Facebook bot detection (show dog website)
        if (detectionResult.isFacebookBot || detectionResult.showDogWebsite) {
          console.log('🤖📘 Facebook bot confirmed - showing dog website');
          setShowDogWebsite(true);
          return;
        }
        
        // Priority 2: High confidence bot detection
        if (detectionResult.isBot && detectionResult.confidence >= 0.8) {
          console.log('🤖 High confidence bot - showing bot content');
          setShowBot(true);
          return;
        }
        
        // Priority 3: Medium confidence bots (show dog website for SEO)
        if (detectionResult.isBot && detectionResult.confidence >= 0.6) {
          console.log('🤖 Medium confidence bot - showing dog website');
          setShowDogWebsite(true);
          return;
        }
        
        // Human detection logic (enhanced)
        const humanIndicators = (
          behaviorMetrics.mouseMovements > 3 ||
          behaviorMetrics.keyboardEvents > 0 ||
          behaviorMetrics.scrollBehavior > 0 ||
          behaviorMetrics.touchEvents > 0
        );
        
        const isLikelyHuman = (
          detectionResult.confidence < 0.4 && 
          behaviorMetrics.timeSpent > 3000 &&
          humanIndicators
        );
        
        if (isLikelyHuman) {
          if (!redirecting && !showBot && !showDogWebsite) {
            console.log('👤 Human detected - redirecting to main site');
            setRedirecting(true);
            // Faster redirect for confirmed humans
            setTimeout(() => {
              window.location.href = "http://localhost:5173";
            }, 1000);
          }
        }
        
        // Extended analysis for uncertain cases
        if (detectionResult.confidence < 0.5 && behaviorMetrics.timeSpent > 8000) {
          if (!redirecting && !showBot && !showDogWebsite) {
            console.log('👤 Extended human analysis - redirecting');
            setRedirecting(true);
            setTimeout(() => {
              window.location.href = "http://localhost:5173";
            }, 800);
          }
        }
      }
    };

    checkDetectionResult();
  }, [detectionResult, behaviorMetrics, redirecting, showBot, showDogWebsite]);

  // Debug mode - enhanced with backend data
  if (debugMode) {
    return (
      <div className="min-h-screen bg-gray-100 p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-6">🔍 Enhanced Bot Detection Debug Mode</h1>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-bold mb-4">Detection Result</h2>
              <pre className="text-sm overflow-auto bg-gray-50 p-4 rounded">
                {JSON.stringify(detectionResult, null, 2)}
              </pre>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-bold mb-4">Behavior Metrics</h2>
              <pre className="text-sm overflow-auto bg-gray-50 p-4 rounded">
                {JSON.stringify(behaviorMetrics, null, 2)}
              </pre>
            </div>
          </div>

          {/* Backend Communication Status */}
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <h2 className="text-xl font-bold mb-4">Backend Communication</h2>
            <div className="space-y-2">
              <div className={`flex items-center gap-2 ${
                detectionResult.backendVerified ? 'text-green-600' : 'text-red-600'
              }`}>
                <div className={`w-3 h-3 rounded-full ${
                  detectionResult.backendVerified ? 'bg-green-500' : 'bg-red-500'
                }`}></div>
                <span>
                  Backend {detectionResult.backendVerified ? 'Connected' : 'Not Connected'}
                </span>
              </div>
              
              {detectionResult.backendResult && (
                <div className="mt-4 p-4 bg-gray-50 rounded">
                  <h3 className="font-semibold mb-2">Backend Response:</h3>
                  <pre className="text-xs overflow-auto">
                    {JSON.stringify(detectionResult.backendResult, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <h2 className="text-xl font-bold mb-4">Browser Information</h2>
            <div className="space-y-2 text-sm">
              <div><strong>User Agent:</strong> {navigator.userAgent}</div>
              <div><strong>Platform:</strong> {navigator.platform}</div>
              <div><strong>Languages:</strong> {navigator.languages?.join(', ')}</div>
              <div><strong>Hardware Concurrency:</strong> {navigator.hardwareConcurrency}</div>
              <div><strong>Max Touch Points:</strong> {navigator.maxTouchPoints}</div>
              <div><strong>WebDriver:</strong> {(navigator as any).webdriver ? 'Present' : 'Not Present'}</div>
            </div>
          </div>
          
          <div className="flex flex-wrap gap-4">
            <button 
              onClick={() => setShowBot(true)}
              className="bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors"
            >
              Show Bot Content
            </button>
            <button 
              onClick={() => setShowDogWebsite(true)}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Show Dog Website
            </button>
            <button 
              onClick={() => window.location.href = "http://localhost:5173"}
              className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors"
            >
              Redirect to Main Site
            </button>
            <button 
              onClick={() => window.location.reload()}
              className="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition-colors"
            >
              Restart Analysis
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Show dog website for Facebook bots and medium confidence bots
  if (showDogWebsite) {
    return <DogFoodWebsite detectionResult={detectionResult} behaviorMetrics={behaviorMetrics} />;
  }

  // Show bot content for high confidence non-Facebook bots or blocked requests
  if (showBot) {
    return <BotContent detectionResult={detectionResult} behaviorMetrics={behaviorMetrics} />;
  }

  // Show enhanced loader for humans (while detecting and before redirect)
  return <EnhancedLoader />;
};

export default App;