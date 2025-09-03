#!/usr/bin/env python3
"""
FINAL Bot Detection Test - Server-side routing through Django
SUCCESS = Bots redirected to 3000, Humans redirected to 3001
"""

import requests
import time

def test_django_routing():
    """Test the new Django-based traffic routing"""
    
    print("🛡️  Testing Django Traffic Routing")
    print("=" * 50)
    print("Flow: All traffic → Django (8000) → Bot detection → Route accordingly")
    
    # Test 1: Facebook Bot → Should be redirected to 3000
    print("\n1. Testing Facebook Bot...")
    try:
        bot_response = requests.get(
            "http://localhost:8000",
            headers={"User-Agent": "facebookexternalhit/1.1"},
            allow_redirects=True,
            timeout=10
        )
        
        print(f"   Status: {bot_response.status_code}")
        print(f"   Final URL: {bot_response.url}")
        
        bot_redirected = ":3000" in bot_response.url
        
        print(f"   Bot redirected to 3000: {'✅ YES' if bot_redirected else '❌ NO'}")
        
        if bot_redirected:
            print(f"   ✅ Bot was routed correctly to bot-specific port (3000)")
        
    except Exception as e:
        print(f"   ❌ Bot test failed: {e}")
        bot_redirected = False
    
    # Test 2: Normal Browser → Should be redirected to main site at port 3001
    print("\n2. Testing Normal Browser...")
    try:
        human_response = requests.get(
            "http://localhost:8000",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124"},
            allow_redirects=True,
            timeout=10
        )
        
        print(f"   Status: {human_response.status_code}")
        print(f"   Final URL: {human_response.url}")
        
        human_redirected = ":3001" in human_response.url
        
        print(f"   Human redirected to 3001: {'✅ YES' if human_redirected else '❌ NO'}")
        
        if human_redirected:
            print(f"   ✅ Human reached main site at port 3001")
        
    except Exception as e:
        print(f"   ❌ Human test failed: {e}")
        human_redirected = False
    
    # Test 3: Test various bot types
    print("\n3. Testing Other Bot Types...")
    other_bots = [
        ("Googlebot", "Mozilla/5.0 (compatible; Googlebot/2.1)"),
        ("Python Script", "python-requests/2.25.1"),
        ("Curl", "curl/7.68.0"),
        ("Empty UA", ""),
    ]
    
    bot_detection_count = 0
    for bot_name, bot_ua in other_bots:
        try:
            response = requests.get(
                "http://localhost:8000",
                headers={"User-Agent": bot_ua},
                allow_redirects=True,
                timeout=5
            )
            
            detected = ":3000" in response.url or "security" in response.text.lower()
            print(f"   {bot_name}: {'✅ Redirected to 3000 or blocked' if detected else '❌ MISSED'}")
            
            if detected:
                bot_detection_count += 1
                
        except Exception as e:
            print(f"   {bot_name}: ❌ Error - {e}")
    
    other_bots_blocked = bot_detection_count >= len(other_bots) // 2
    
    overall_success = bot_redirected and human_redirected and other_bots_blocked
    
    print(f"\n{'🎉 SUCCESS!' if overall_success else '❌ ISSUES FOUND!'}")
    
    if overall_success:
        print("✅ Django traffic routing working correctly!")
        print("✅ Bots are redirected to port 3000")
        print("✅ Humans are redirected to main site on port 3001")
        print("✅ Multiple bot types detected and routed")
    else:
        print("❌ Issues:")
        if not bot_redirected:
            print("   • Facebook bot not redirected to port 3000")
        if not human_redirected:
            print("   • Humans not redirected to port 3001")
        if not other_bots_blocked:
            print("   • Some bots are getting through unfiltered")
    
    return overall_success

def test_old_direct_access():
    """Test that old direct access still works as fallback"""
    print(f"\n🔄 Testing Direct Access (Fallback)...")
    
    try:
        direct_response = requests.get("http://localhost:3001", timeout=5)
        direct_works = direct_response.status_code == 200
        print(f"   Direct access to 3001: {'✅ Works' if direct_works else '❌ Blocked'}")
        return direct_works
    except Exception as e:
        print(f"   Direct access failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Final Bot Detection Test")
    print("Testing server-side bot detection with Django routing")
    
    try:
        health_check = requests.get("http://localhost:8000/api/bot-detection/health/", timeout=5)
        django_running = health_check.status_code == 200
        print(f"Django backend: {'✅ Running' if django_running else '❌ Down'}")
    except:
        print("❌ Django backend not running on port 8000!")
        print("   Start with: python manage.py runserver 8000")
        exit(1)
    
    main_success = test_django_routing()
    fallback_works = test_old_direct_access()
    
    print(f"\n{'🎉 SYSTEM WORKING!' if main_success else '❌ NEEDS FIXES!'}")
    
    if main_success:
        print("\n🔧 New Traffic Flow:")
        print("1. All traffic goes to Django (port 8000)")
        print("2. Django detects bots server-side")
        print("3. Bots → Redirected to port 3000")
        print("4. Humans → Redirected to main site (port 3001)")
        print("5. ✅ Real bots are now properly handled!")
    else:
        print("\n🔧 Debugging:")
        print("1. Make sure you added the TrafficRoutingMiddleware")
        print("2. Restart Django server after adding middleware")
        print("3. Check Django logs for any errors")
        print("4. Verify the middleware routing logic (3000 for bots, 3001 for humans)")
