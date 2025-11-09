#!/usr/bin/env python
"""
Load Testing Script for VPBank Voice Agent
Tests concurrent requests and measures performance
"""
import asyncio
import aiohttp
import time
from statistics import mean, median

async def test_browser_agent(session, request_id):
    """Test browser agent endpoint"""
    start = time.time()
    try:
        async with session.get('http://localhost:7863/api/health', timeout=aiohttp.ClientTimeout(total=10)) as resp:
            duration = time.time() - start
            return {"id": request_id, "status": resp.status, "duration": duration, "success": resp.status == 200}
    except Exception as e:
        return {"id": request_id, "status": 0, "duration": time.time() - start, "success": False, "error": str(e)}

async def test_voice_bot(session, request_id):
    """Test voice bot WebRTC endpoint"""
    start = time.time()
    try:
        payload = {"sdp": "v=0", "type": "offer"}
        async with session.post('http://localhost:7860/offer', json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            duration = time.time() - start
            return {"id": request_id, "status": resp.status, "duration": duration, "success": resp.status == 200}
    except Exception as e:
        return {"id": request_id, "status": 0, "duration": time.time() - start, "success": False, "error": str(e)}

async def run_load_test(concurrent_requests=10, total_requests=100):
    """Run load test with specified concurrency"""
    print(f"🚀 Starting load test: {total_requests} requests, {concurrent_requests} concurrent")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Test Browser Agent
        print("\n📊 Testing Browser Agent...")
        tasks = [test_browser_agent(session, i) for i in range(total_requests)]
        browser_results = []
        for i in range(0, len(tasks), concurrent_requests):
            batch = await asyncio.gather(*tasks[i:i+concurrent_requests])
            browser_results.extend(batch)
        
        # Test Voice Bot
        print("📊 Testing Voice Bot...")
        tasks = [test_voice_bot(session, i) for i in range(total_requests)]
        voice_results = []
        for i in range(0, len(tasks), concurrent_requests):
            batch = await asyncio.gather(*tasks[i:i+concurrent_requests])
            voice_results.extend(batch)
    
    # Calculate statistics
    def analyze(results, name):
        success = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        durations = [r["duration"] for r in success]
        
        print(f"\n{'='*60}")
        print(f"📈 {name} Results:")
        print(f"{'='*60}")
        print(f"✅ Successful: {len(success)}/{len(results)} ({len(success)/len(results)*100:.1f}%)")
        print(f"❌ Failed: {len(failed)}")
        if durations:
            print(f"⏱️  Response Time:")
            print(f"   - Average: {mean(durations)*1000:.2f}ms")
            print(f"   - Median: {median(durations)*1000:.2f}ms")
            print(f"   - Min: {min(durations)*1000:.2f}ms")
            print(f"   - Max: {max(durations)*1000:.2f}ms")
        if failed:
            print(f"⚠️  Errors: {failed[0].get('error', 'Unknown')}")
    
    analyze(browser_results, "Browser Agent")
    analyze(voice_results, "Voice Bot")
    
    print(f"\n{'='*60}")
    print("✅ Load test completed!")

if __name__ == '__main__':
    import sys
    concurrent = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    total = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    
    asyncio.run(run_load_test(concurrent, total))
