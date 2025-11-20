#!/usr/bin/env python3
"""
Minimal test script for browser-use debugging
Based on: https://github.com/browser-use/browser-use
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_basic_browser():
    """Test 1: Basic browser initialization"""
    print("=" * 60)
    print("TEST 1: Basic Browser Initialization")
    print("=" * 60)
    
    try:
        from browser_use import Browser
        
        print("✅ Imported Browser")
        
        # Create browser with minimal config
        browser = Browser(
            headless=True,
            disable_security=True,
        )
        
        print("✅ Created Browser instance")
        print(f"   Browser: {browser}")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_browser_with_agent():
    """Test 2: Browser with Agent"""
    print("\n" + "=" * 60)
    print("TEST 2: Browser with Agent")
    print("=" * 60)
    
    try:
        from browser_use import Agent, Browser
        from browser_use.llm import ChatOpenAI
        
        print("✅ Imported Agent, Browser, ChatOpenAI")
        
        # Create LLM
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY not found")
            return False
        
        llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=api_key)
        print("✅ Created ChatOpenAI")
        
        # Create browser
        browser = Browser(
            headless=True,
            disable_security=True,
        )
        print("✅ Created Browser")
        
        # Create agent with simple task
        agent = Agent(
            task="Go to google.com",
            llm=llm,
            browser=browser,
        )
        print("✅ Created Agent")
        
        # Try to run (with timeout)
        print("🚀 Running agent (max 60s)...")
        result = await asyncio.wait_for(agent.run(max_steps=3), timeout=60)
        
        print(f"✅ Agent completed!")
        print(f"   Result: {result}")
        
        return True
        
    except asyncio.TimeoutError:
        print("❌ Agent timed out after 60s")
        return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_playwright_direct():
    """Test 3: Direct Playwright test"""
    print("\n" + "=" * 60)
    print("TEST 3: Direct Playwright Test")
    print("=" * 60)
    
    try:
        from playwright.async_api import async_playwright
        
        print("✅ Imported Playwright")
        
        async with async_playwright() as p:
            print("✅ Started Playwright")
            
            browser = await p.chromium.launch(headless=True)
            print("✅ Launched Chromium")
            
            page = await browser.new_page()
            print("✅ Created page")
            
            await page.goto("https://www.google.com", timeout=10000)
            print("✅ Navigated to Google")
            
            title = await page.title()
            print(f"✅ Page title: {title}")
            
            await browser.close()
            print("✅ Closed browser")
            
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n🔬 BROWSER-USE DEBUG TESTS")
    print("=" * 60)
    print(f"Python: {os.sys.version}")
    print(f"DISPLAY: {os.getenv('DISPLAY', 'Not set')}")
    print(f"BROWSER_HEADLESS: {os.getenv('BROWSER_HEADLESS', 'Not set')}")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Basic browser
    results['basic_browser'] = await test_basic_browser()
    
    # Test 2: Playwright direct (to verify Playwright works)
    results['playwright_direct'] = await test_playwright_direct()
    
    # Test 3: Browser with Agent (only if previous tests pass)
    if results['basic_browser'] and results['playwright_direct']:
        results['browser_with_agent'] = await test_browser_with_agent()
    else:
        print("\n⚠️  Skipping agent test due to previous failures")
        results['browser_with_agent'] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    print("=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
