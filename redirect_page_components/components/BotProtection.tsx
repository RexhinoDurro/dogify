// components/BotProtection.tsx
import React, { useEffect, useState } from 'react';
import { useBotDetection } from '../hooks/useBotDetection';

interface BotProtectionProps {
  children: React.ReactNode;
  onBotDetected?: (result: any) => void;
  strictMode?: boolean;
}

const BotProtection: React.FC<BotProtectionProps> = ({ 
  children, 
  onBotDetected, 
  strictMode = false 
}) => {
  const { detectionResult, behaviorMetrics } = useBotDetection();
  const [isBlocked, setIsBlocked] = useState(false);
  const [showWarning, setShowWarning] = useState(false);

  useEffect(() => {
    if (detectionResult.isBot) {
      const threshold = strictMode ? 0.6 : 0.8;
      
      if (detectionResult.confidence >= threshold) {
        setIsBlocked(true);
        onBotDetected?.(detectionResult);
        
        // Additional security measures
        document.body.style.display = 'none';
        console.clear();
        
        // Report to backend immediately
        reportBotDetection(detectionResult);
      } else if (detectionResult.confidence >= 0.5) {
        setShowWarning(true);
        setTimeout(() => setShowWarning(false), 5000);
      }
    }
  }, [detectionResult, strictMode, onBotDetected]);

  const reportBotDetection = async (result: any) => {
    try {
      await fetch('/api/security/bot-detected', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...result,
          ip: await getClientIP(),
          timestamp: new Date().toISOString(),
          page: window.location.href,
          referrer: document.referrer,
          behavioral: behaviorMetrics
        })
      });
    } catch (error) {
      console.error('Failed to report bot:', error);
    }
  };

  const getClientIP = async (): Promise<string> => {
    try {
      const response = await fetch('/api/get-ip');
      const data = await response.json();
      return data.ip || 'unknown';
    } catch {
      return 'unknown';
    }
  };

  if (isBlocked) {
    return (
      <div className="min-h-screen bg-red-50 flex items-center justify-center">
        <div className="max-w-md mx-auto text-center p-8">
          <div className="text-red-600 text-6xl mb-4">🤖</div>
          <h1 className="text-2xl font-bold text-red-800 mb-4">
            Access Denied
          </h1>
          <p className="text-red-600 mb-4">
            Our security system has detected automated behavior.
          </p>
          <div className="bg-red-100 border border-red-300 rounded p-4 mb-4">
            <p className="text-sm text-red-700">
              <strong>Detection Confidence:</strong> {Math.round(detectionResult.confidence * 100)}%
            </p>
            <p className="text-sm text-red-700 mt-2">
              <strong>Methods:</strong> {detectionResult.detectionMethods.slice(0, 2).join(', ')}
            </p>
          </div>
          <p className="text-gray-600 text-sm">
            If you believe this is an error, please contact support.
          </p>
        </div>
      </div>
    );
  }

  return (
    <>
      {showWarning && (
        <div className="fixed top-4 right-4 bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded shadow-lg z-50">
          <div className="flex items-center">
            <span className="text-xl mr-2">⚠️</span>
            <div>
              <p className="font-medium">Security Alert</p>
              <p className="text-sm">Unusual activity detected</p>
            </div>
          </div>
        </div>
      )}
      
      <div className="bot-protected-content">
        {children}
        
        {/* Hidden honeypot elements for bot detection */}
        <div style={{ position: 'absolute', left: '-9999px', opacity: 0 }}>
          <input type="text" name="honeypot_field" tabIndex={-1} autoComplete="off" />
          <a href="mailto:trap@example.com">Contact</a>
          <button onClick={() => console.log('bot trapped')}>Hidden Button</button>
        </div>
      </div>
    </>
  );
};

export default BotProtection;