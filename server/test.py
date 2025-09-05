from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import random
import json
from datetime import datetime

class BotDetectionTester:
    def __init__(self, url, test_type="aggressive"):
        self.url = url
        self.test_type = test_type
        self.results = []
        
    def setup_bot_browser(self, stealth_level="obvious"):
        """Setup Chrome with different bot detection evasion levels"""
        options = Options()
        
        if stealth_level == "obvious":
            # Make it obvious we're a bot
            options.add_argument("--user-agent=BotTester/1.0 (Testing Bot Detection)")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
        elif stealth_level == "moderate":
            # Some bot-like behavior but try to hide
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            options.add_argument("--disable-blink-features=AutomationControlled")
            
        elif stealth_level == "stealth":
            # Try to look human
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
        options.add_argument("--start-maximized")
        return webdriver.Chrome(options=options)
    
    def bot_behavior_test(self, driver, behavior_type):
        """Different bot-like behaviors to test detection"""
        
        if behavior_type == "rapid_clicking":
            print("🤖 Testing: Rapid clicking behavior")
            try:
                links = driver.find_elements(By.TAG_NAME, "a")[:5]
                for link in links:
                    link.click()
                    time.sleep(0.1)  # Very fast clicking
                    driver.back()
                    time.sleep(0.1)
            except Exception as e:
                print(f"Error in rapid clicking: {e}")
        
        elif behavior_type == "no_mouse_movement":
            print("🤖 Testing: No mouse movement (pure keyboard)")
            # Just navigate without any mouse simulation
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, 0);")
        
        elif behavior_type == "perfect_timing":
            print("🤖 Testing: Perfect timing patterns")
            for i in range(5):
                driver.refresh()
                time.sleep(2.0)  # Exactly 2 seconds each time
        
        elif behavior_type == "form_spam":
            print("🤖 Testing: Form submission spam")
            try:
                forms = driver.find_elements(By.TAG_NAME, "form")
                for form in forms[:3]:
                    inputs = form.find_elements(By.TAG_NAME, "input")
                    for inp in inputs:
                        if inp.get_attribute("type") in ["text", "email"]:
                            inp.send_keys("bot@test.com")
                    time.sleep(0.5)
            except Exception as e:
                print(f"Error in form spam: {e}")
        
        elif behavior_type == "suspicious_headers":
            print("🤖 Testing: Suspicious headers (via JavaScript)")
            driver.execute_script("""
                // Try to detect if we're being detected
                console.log('Bot test - checking for detection');
                if (navigator.webdriver) {
                    console.log('Navigator.webdriver detected!');
                }
            """)
    
    def human_behavior_test(self, driver):
        """Simulate more human-like behavior"""
        print("👨 Testing: Human-like behavior")
        
        # Random scrolling
        for _ in range(3):
            scroll_amount = random.randint(100, 500)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.5, 2.0))
        
        # Random delays
        time.sleep(random.uniform(1, 3))
        
        # Click with random delays
        try:
            links = driver.find_elements(By.TAG_NAME, "a")
            if links:
                link = random.choice(links[:3])
                time.sleep(random.uniform(0.5, 1.5))
                link.click()
                time.sleep(random.uniform(2, 4))
                driver.back()
        except Exception:
            pass
    
    def check_bot_detection(self, driver):
        """Check if the website detected us as a bot"""
        detection_indicators = {
            'captcha': False,
            'blocked': False,
            'rate_limited': False,
            'suspicious_redirect': False
        }
        
        current_url = driver.current_url
        page_source = driver.page_source.lower()
        
        # Check for common bot detection indicators
        if 'captcha' in page_source or 'recaptcha' in page_source:
            detection_indicators['captcha'] = True
            print("🚨 CAPTCHA detected!")
        
        if 'blocked' in page_source or 'access denied' in page_source:
            detection_indicators['blocked'] = True
            print("🚨 Access blocked!")
        
        if 'rate limit' in page_source or 'too many requests' in page_source:
            detection_indicators['rate_limited'] = True
            print("🚨 Rate limited!")
        
        if current_url != self.url and 'cloudflare' in current_url:
            detection_indicators['suspicious_redirect'] = True
            print("🚨 Suspicious redirect (possibly Cloudflare)!")
        
        # Check response time (bots often get delayed responses)
        start_time = time.time()
        driver.refresh()
        load_time = time.time() - start_time
        
        if load_time > 10:
            print(f"🚨 Slow response time: {load_time:.2f}s (possible bot throttling)")
        
        return detection_indicators
    
    def run_comprehensive_test(self):
        """Run comprehensive bot detection tests"""
        test_scenarios = [
            ("obvious", "rapid_clicking"),
            ("obvious", "no_mouse_movement"),
            ("obvious", "perfect_timing"),
            ("obvious", "form_spam"),
            ("moderate", "rapid_clicking"),
            ("stealth", "human_like"),
        ]
        
        print(f"🔍 Starting bot detection tests on: {self.url}")
        print("=" * 60)
        
        for stealth_level, behavior in test_scenarios:
            print(f"\n📋 Test: {stealth_level.upper()} stealth + {behavior.replace('_', ' ').title()}")
            print("-" * 40)
            
            driver = self.setup_bot_browser(stealth_level)
            
            try:
                # Navigate to site
                print(f"🌐 Navigating to {self.url}")
                driver.get(self.url)
                time.sleep(2)
                
                # Take initial screenshot
                screenshot_name = f"test_{stealth_level}_{behavior}_{int(time.time())}.png"
                driver.save_screenshot(screenshot_name)
                print(f"📸 Screenshot saved: {screenshot_name}")
                
                # Perform bot behavior
                if behavior == "human_like":
                    self.human_behavior_test(driver)
                else:
                    self.bot_behavior_test(driver, behavior)
                
                # Check for detection
                detection_result = self.check_bot_detection(driver)
                
                # Record results
                test_result = {
                    'timestamp': datetime.now().isoformat(),
                    'stealth_level': stealth_level,
                    'behavior': behavior,
                    'detection_indicators': detection_result,
                    'screenshot': screenshot_name,
                    'final_url': driver.current_url
                }
                
                self.results.append(test_result)
                
                # Show live results
                detected = any(detection_result.values())
                status = "🔴 DETECTED" if detected else "🟢 NOT DETECTED"
                print(f"Result: {status}")
                
                if detected:
                    detected_methods = [k for k, v in detection_result.items() if v]
                    print(f"Detection methods: {', '.join(detected_methods)}")
                
                # Wait before next test
                print("⏳ Waiting 5 seconds before next test...")
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ Error in test: {e}")
            
            finally:
                driver.quit()
        
        # Save detailed results
        with open('bot_detection_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📊 All tests completed! Results saved to bot_detection_results.json")
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 BOT DETECTION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        detected_tests = sum(1 for r in self.results if any(r['detection_indicators'].values()))
        
        print(f"Total tests run: {total_tests}")
        print(f"Bot detection triggered: {detected_tests}")
        print(f"Detection rate: {(detected_tests/total_tests)*100:.1f}%")
        
        print("\nDetection breakdown:")
        for result in self.results:
            detected = any(result['detection_indicators'].values())
            status = "🔴" if detected else "🟢"
            print(f"{status} {result['stealth_level']} + {result['behavior']}")

# Usage
if __name__ == "__main__":
    # Replace with your website URL
    website_url = input("Enter your website URL: ").strip()
    if not website_url.startswith('http'):
        website_url = 'http://' + website_url
    
    tester = BotDetectionTester(website_url)
    tester.run_comprehensive_test()