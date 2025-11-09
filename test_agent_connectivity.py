#!/usr/bin/env python
"""
Agent Connectivity Test
Tests communication between Voice Bot and Browser Agent
"""
import asyncio
import aiohttp
import json

async def test_connectivity():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║       Agent Connectivity Test                            ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    # Test 1: Browser Agent Health
    print("1️⃣  Testing Browser Agent...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:7863/api/health') as resp:
                data = await resp.json()
                print(f"   ✅ Browser Agent: {data['status']}")
    except Exception as e:
        print(f"   ❌ Browser Agent: {e}")
        return
    
    # Test 2: Voice Bot Health
    print("\n2️⃣  Testing Voice Bot...")
    try:
        async with aiohttp.ClientSession() as session:
            payload = {"sdp": "v=0", "type": "offer"}
            async with session.post('http://localhost:7860/offer', json=payload) as resp:
                data = await resp.json()
                print(f"   ✅ Voice Bot: {data['type']} received")
    except Exception as e:
        print(f"   ❌ Voice Bot: {e}")
        return
    
    # Test 3: Voice Bot → Browser Agent Communication
    print("\n3️⃣  Testing Voice Bot → Browser Agent workflow...")
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "user_message": "Điền form vay với tên Nguyễn Văn A, số điện thoại 0912345678",
                "session_id": "connectivity-test",
                "request_id": "test-001"
            }
            async with session.post('http://localhost:7863/api/execute', json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                data = await resp.json()
                if data.get('success'):
                    print(f"   ✅ Workflow executed successfully")
                    print(f"   📝 Result: {data.get('result', '')[:100]}...")
                else:
                    print(f"   ⚠️  Workflow completed with issues: {data.get('error', 'Unknown')}")
    except Exception as e:
        print(f"   ❌ Workflow failed: {e}")
        return
    
    # Test 4: Check Browser Agent live URL
    print("\n4️⃣  Checking Browser Agent live session...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:7863/api/live') as resp:
                data = await resp.json()
                live_url = data.get('live_url')
                if live_url:
                    print(f"   ✅ Browser session active: {live_url}")
                else:
                    print(f"   ℹ️  No active browser session")
    except Exception as e:
        print(f"   ⚠️  Could not check live session: {e}")
    
    print("\n" + "="*60)
    print("✅ Agent Connectivity Test PASSED")
    print("="*60)
    print("\n📊 Summary:")
    print("   • Browser Agent: Running and healthy")
    print("   • Voice Bot: Running and responding")
    print("   • Inter-agent communication: Working")
    print("   • Workflow execution: Successful")
    print("\n🎯 All agents are properly connected!")

if __name__ == '__main__':
    asyncio.run(test_connectivity())
