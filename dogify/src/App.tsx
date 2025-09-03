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

// Import the enhanced bot detection hook and types
import useEnhancedBotDetection, { type DetectionResult, type BehaviorMetrics } from './hooks/useEnhancedBotDetection';

// Component prop interfaces
interface BotContentProps {
  detectionResult: DetectionResult;
  behaviorMetrics: BehaviorMetrics;
}

interface DogFoodWebsiteProps {
  detectionResult: DetectionResult;
  behaviorMetrics: BehaviorMetrics;
}

// Minimal Loading Spinner (Clean & Fast)
const MinimalLoader: React.FC = () => (
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
        Checking access permissions...
      </div>
    </div>
  </div>
);

// Bot Content (Only shown to detected bots, especially Facebook bots)
const BotContent: React.FC<BotContentProps> = ({ detectionResult, behaviorMetrics }) => {
  const isFacebookBot = detectionResult.detectionMethods.some((method: string) => 
    method.includes('facebook') || method.includes('facebot')
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-800 via-purple-800 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="mb-8">
            <div className="inline-flex items-center justify-center w-24 h-24 bg-white/10 backdrop-blur-lg rounded-full mb-6 border border-white/20">
              <span className="text-4xl">{isFacebookBot ? '🤖📘' : '🤖'}</span>
            </div>
            
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-4">
              Welcome to Dogify
            </h1>
            
            {isFacebookBot && (
              <div className="bg-blue-600/20 backdrop-blur-lg rounded-xl p-4 mb-6 border border-blue-400/30">
                <h2 className="text-2xl font-bold text-blue-200 mb-2">Facebook Bot Detected</h2>
                <p className="text-blue-100">
                  Hello Facebook crawler! You're viewing the bot-optimized version of our dog food store.
                </p>
              </div>
            )}
            
            <p className="text-lg text-white/80 mb-6 max-w-2xl mx-auto">
              Premium nutrition for your furry friends. Automated access detected - showing optimized content.
            </p>
          </div>
          
          {/* Dog Food Products for Bots (SEO Optimized) */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <div className="text-4xl mb-4">🥘</div>
              <h3 className="text-xl font-bold text-white mb-2">Premium Dry Food</h3>
              <p className="text-white/70 mb-3">High-quality grain-free nutrition for adult dogs</p>
              <div className="text-green-400 font-bold text-lg">From $49.99</div>
            </div>
            
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <div className="text-4xl mb-4">🦴</div>
              <h3 className="text-xl font-bold text-white mb-2">Training Treats</h3>
              <p className="text-white/70 mb-3">Delicious rewards for good behavior</p>
              <div className="text-green-400 font-bold text-lg">From $12.99</div>
            </div>
            
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <div className="text-4xl mb-4">🥫</div>
              <h3 className="text-xl font-bold text-white mb-2">Wet Food Variety</h3>
              <p className="text-white/70 mb-3">Nutritious and tasty wet food options</p>
              <div className="text-green-400 font-bold text-lg">From $32.99</div>
            </div>
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
                <span>Backend Verified:</span>
                <span className="font-mono">{detectionResult.backendVerified ? 'Yes' : 'No'}</span>
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
            🔒 Advanced Multi-Layer Bot Detection System with Backend Verification
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
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main Dog Food Website (shown to bots)
const DogFoodWebsite: React.FC<DogFoodWebsiteProps> = ({ detectionResult }) => (
  <CartProvider>
    <WishlistProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Header />
          <main>
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
          
          {/* Debug info for detected bots */}
          {detectionResult.isBot && (
            <div className="fixed bottom-4 right-4 bg-red-600 text-white p-2 rounded text-xs max-w-xs">
              Bot Detected: {Math.round(detectionResult.confidence * 100)}% confidence
              {detectionResult.backendVerified && <div>Backend Verified ✓</div>}
            </div>
          )}
        </div>
      </Router>
    </WishlistProvider>
  </CartProvider>
);

// Main App Component
const App: React.FC = () => {
  const [redirecting, setRedirecting] = useState<boolean>(false);
  const [showBot, setShowBot] = useState<boolean>(false);
  const [showDogWebsite, setShowDogWebsite] = useState<boolean>(false);
  const [debugMode, setDebugMode] = useState<boolean>(false);
  
  const { detectionResult, behaviorMetrics } = useEnhancedBotDetection();

  // Enable debug mode with URL parameter
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    setDebugMode(urlParams.get('debug') === 'true');
  }, []);

  useEffect(() => {
    const checkDetectionResult = () => {
      if (detectionResult.confidence > 0) {
        console.log('🔍 Detection result:', detectionResult);
        
        // Check if backend blocked the request
        if (detectionResult.backendResult?.blocked) {
          console.log('🚫 Backend blocked - showing bot content');
          setShowBot(true);
          return;
        }
        
        // High confidence bot detection (especially Facebook bots)
        if (detectionResult.isBot && detectionResult.confidence >= 0.7) {
          const isFacebookBot = detectionResult.detectionMethods.some((method: string) => 
            method.includes('facebook') || method.includes('facebot') || method.includes('facebookexternalhit')
          );
          
          if (isFacebookBot) {
            console.log('🤖📘 Facebook bot confirmed - showing dog website');
            setShowDogWebsite(true);
          } else {
            console.log('🤖 High confidence bot - showing bot content');
            setShowBot(true);
          }
          return;
        }
        
        // Medium confidence bots - show dog website
        if (detectionResult.isBot && detectionResult.confidence >= 0.5) {
          console.log('🤖 Medium confidence bot - showing dog website');
          setShowDogWebsite(true);
          return;
        }
        
        // Human detection logic
        if (detectionResult.confidence < 0.3 && behaviorMetrics.timeSpent > 2000) {
          // Low bot confidence + some interaction time = likely human
          if (!redirecting && !showBot && !showDogWebsite) {
            console.log('👤 Human detected - redirecting to main site');
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
          if (!redirecting && !showBot && !showDogWebsite) {
            console.log('👤 Human activity confirmed - redirecting');
            setRedirecting(true);
            setTimeout(() => {
              window.location.href = "http://localhost:5173";
            }, 600);
          }
        }
      }
    };

    checkDetectionResult();
  }, [detectionResult, behaviorMetrics, redirecting, showBot, showDogWebsite]);

  // Debug mode - show detection info
  if (debugMode) {
    return (
      <div className="min-h-screen bg-gray-100 p-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-6">🔍 Bot Detection Debug Mode</h1>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-bold mb-4">Detection Result</h2>
              <pre className="text-sm overflow-auto">
                {JSON.stringify(detectionResult, null, 2)}
              </pre>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-bold mb-4">Behavior Metrics</h2>
              <pre className="text-sm overflow-auto">
                {JSON.stringify(behaviorMetrics, null, 2)}
              </pre>
            </div>
          </div>
          
          <div className="mt-6 bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">User Agent</h2>
            <p className="text-sm break-all">{navigator.userAgent}</p>
          </div>
          
          <div className="mt-6 text-center space-x-4">
            <button 
              onClick={() => setShowBot(true)}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Show Bot Content
            </button>
            <button 
              onClick={() => setShowDogWebsite(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Show Dog Website
            </button>
            <button 
              onClick={() => window.location.href = "http://localhost:5173"}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
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
    return <DogFoodWebsite detectionResult={detectionResult} behaviorMetrics={behaviorMetrics} />;
  }

  // Show bot content for high confidence non-Facebook bots
  if (showBot) {
    return <BotContent detectionResult={detectionResult} behaviorMetrics={behaviorMetrics} />;
  }

  // Show minimal loader for humans (while detecting and before redirect)
  return <MinimalLoader />;
};

export default App;