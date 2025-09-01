x// src/App.tsx - Enhanced with bot protection
import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import BotProtection from './components/BotProtection'
import { useBotDetection } from './hooks/useBotDetection'

function App() {
  const [count, setCount] = useState(0)
  const [showDebugInfo, setShowDebugInfo] = useState(false)
  const { detectionResult, behaviorMetrics } = useBotDetection()

  const handleBotDetected = (result: any) => {
    console.warn('Bot detected:', result)
    // Additional actions when bot is detected
    // e.g., send analytics, show CAPTCHA, etc.
  }

  // Anti-bot measures
  useEffect(() => {
    // Prevent right-click context menu (basic protection)
    const handleContextMenu = (e: MouseEvent) => {
      e.preventDefault()
    }

    // Prevent common debugging shortcuts
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'F12' || 
          (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'J')) ||
          (e.ctrlKey && e.key === 'U')) {
        e.preventDefault()
      }
    }

    // Detect developer tools
    let devtools = {open: false, orientation: null}
    const threshold = 160

    setInterval(() => {
      if (window.outerHeight - window.innerHeight > threshold || 
          window.outerWidth - window.innerWidth > threshold) {
        if (!devtools.open) {
          devtools.open = true
          console.clear()
          console.warn('Developer tools detected')
        }
      } else {
        devtools.open = false
      }
    }, 500)

    document.addEventListener('contextmenu', handleContextMenu)
    document.addEventListener('keydown', handleKeyDown)

    return () => {
      document.removeEventListener('contextmenu', handleContextMenu)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [])

  return (
    <BotProtection onBotDetected={handleBotDetected} strictMode={true}>
      <div className="min-h-screen bg-gradient-to-br from-purple-400 via-pink-500 to-red-500">
        <div className="container mx-auto px-4 py-8">
          {/* Security Status Bar */}
          <div className="mb-4 p-3 bg-white/20 backdrop-blur-sm rounded-lg border border-white/30">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${
                  detectionResult.confidence < 0.3 ? 'bg-green-400' :
                  detectionResult.confidence < 0.6 ? 'bg-yellow-400' : 'bg-red-400'
                }`}></div>
                <span className="text-white font-medium">
                  Security Status: {
                    detectionResult.confidence < 0.3 ? 'Secure' :
                    detectionResult.confidence < 0.6 ? 'Monitoring' : 'Alert'
                  }
                </span>
              </div>
              <button
                onClick={() => setShowDebugInfo(!showDebugInfo)}
                className="text-white/80 hover:text-white text-sm"
              >
                {showDebugInfo ? 'Hide' : 'Show'} Debug
              </button>
            </div>
            
            {showDebugInfo && (
              <div className="mt-3 p-3 bg-black/20 rounded text-white text-xs font-mono">
                <div>Bot Confidence: {(detectionResult.confidence * 100).toFixed(1)}%</div>
                <div>Mouse Movements: {behaviorMetrics.mouseMovements}</div>
                <div>Keyboard Events: {behaviorMetrics.keyboardEvents}</div>
                <div>Time Spent: {(behaviorMetrics.timeSpent / 1000).toFixed(1)}s</div>
                <div>User Agent: {navigator.userAgent.substring(0, 50)}...</div>
              </div>
            )}
          </div>

          {/* Main Content */}
          <div className="text-center">
            <div className="mb-8">
              <a href="https://vite.dev" target="_blank" rel="noopener noreferrer">
                <img src={viteLogo} className="logo mx-auto" alt="Vite logo" />
              </a>
              <a href="https://react.dev" target="_blank" rel="noopener noreferrer">
                <img src={reactLogo} className="logo react mx-auto" alt="React logo" />
              </a>
            </div>
            
            <h1 className="text-6xl font-bold text-white mb-8 drop-shadow-lg">
              Dogify - Bot Protected
            </h1>
            
            <div className="bg-white/20 backdrop-blur-sm rounded-xl p-8 max-w-md mx-auto border border-white/30">
              <button 
                onClick={() => setCount((count) => count + 1)}
                className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-bold py-3 px-6 rounded-lg transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                count is {count}
              </button>
              
              <p className="text-white/90 mt-4">
                Edit <code className="bg-black/20 px-2 py-1 rounded">src/App.tsx</code> and save to test HMR
              </p>
            </div>

            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto">
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
                <h3 className="text-white font-bold mb-2">🛡️ Bot Detection</h3>
                <p className="text-white/80 text-sm">
                  Advanced ML-powered bot detection with behavioral analysis
                </p>
              </div>
              
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
                <h3 className="text-white font-bold mb-2">🚫 IP Blacklisting</h3>
                <p className="text-white/80 text-sm">
                  Automatic IP blacklisting for detected bots and suspicious activity
                </p>
              </div>
              
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
                <h3 className="text-white font-bold mb-2">📊 Real-time Monitoring</h3>
                <p className="text-white/80 text-sm">
                  Continuous behavioral analysis and threat assessment
                </p>
              </div>
            </div>

            <p className="text-white/70 mt-8">
              Click on the Vite and React logos to learn more
            </p>
          </div>
        </div>
      </div>
    </BotProtection>
  )
}

export default App