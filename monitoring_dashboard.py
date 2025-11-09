#!/usr/bin/env python
"""
Simple Monitoring Dashboard
Real-time health monitoring for all services
"""
import asyncio
import aiohttp
from aiohttp import web
import json
from datetime import datetime

SERVICES = {
    "browser_agent": "http://localhost:7863/api/health",
    "voice_bot": "http://localhost:7860/offer",
    "frontend": "http://localhost:5173"
}

async def check_service(session, name, url):
    """Check service health"""
    try:
        if name == "voice_bot":
            async with session.post(url, json={"sdp": "v=0", "type": "offer"}, timeout=aiohttp.ClientTimeout(total=3)) as resp:
                return {"name": name, "status": "healthy" if resp.status == 200 else "unhealthy", "code": resp.status}
        else:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as resp:
                return {"name": name, "status": "healthy" if resp.status == 200 else "unhealthy", "code": resp.status}
    except Exception as e:
        return {"name": name, "status": "down", "error": str(e)}

async def get_health(request):
    """Get all services health"""
    async with aiohttp.ClientSession() as session:
        tasks = [check_service(session, name, url) for name, url in SERVICES.items()]
        results = await asyncio.gather(*tasks)
    
    return web.json_response({
        "timestamp": datetime.utcnow().isoformat(),
        "services": results,
        "overall": "healthy" if all(r["status"] == "healthy" for r in results) else "degraded"
    })

async def dashboard(request):
    """Serve monitoring dashboard HTML"""
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>VPBank Voice Agent - Monitoring</title>
    <style>
        body { font-family: Arial; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #1a73e8; }
        .service { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .healthy { border-left: 5px solid #34a853; }
        .unhealthy { border-left: 5px solid #ea4335; }
        .down { border-left: 5px solid #fbbc04; }
        .status { font-weight: bold; font-size: 18px; }
        .timestamp { color: #666; font-size: 12px; }
        .refresh { background: #1a73e8; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .refresh:hover { background: #1557b0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎤 VPBank Voice Agent - System Monitor</h1>
        <button class="refresh" onclick="loadHealth()">🔄 Refresh</button>
        <p class="timestamp" id="timestamp"></p>
        <div id="services"></div>
    </div>
    <script>
        async function loadHealth() {
            const resp = await fetch('/api/health');
            const data = await resp.json();
            document.getElementById('timestamp').textContent = 'Last updated: ' + new Date(data.timestamp).toLocaleString();
            
            const html = data.services.map(s => `
                <div class="service ${s.status}">
                    <h3>${s.name.replace('_', ' ').toUpperCase()}</h3>
                    <div class="status">Status: ${s.status.toUpperCase()}</div>
                    ${s.code ? '<p>HTTP: ' + s.code + '</p>' : ''}
                    ${s.error ? '<p style="color: red;">Error: ' + s.error + '</p>' : ''}
                </div>
            `).join('');
            
            document.getElementById('services').innerHTML = html;
        }
        
        loadHealth();
        setInterval(loadHealth, 5000);
    </script>
</body>
</html>
    """
    return web.Response(text=html, content_type='text/html')

app = web.Application()
app.router.add_get('/', dashboard)
app.router.add_get('/api/health', get_health)

if __name__ == '__main__':
    print("🔍 Starting Monitoring Dashboard on http://localhost:8888")
    web.run_app(app, host='0.0.0.0', port=8888)
