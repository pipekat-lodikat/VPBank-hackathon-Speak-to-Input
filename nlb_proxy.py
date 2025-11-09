#!/usr/bin/env python3
"""
Simple HTTP/WebSocket Proxy to NLB
Forwards all requests to VPBank Voice Agent NLB
"""

import aiohttp
from aiohttp import web
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NLB endpoint
NLB_VOICE_BOT = "http://vpbank-voice-agent-nlb-b65730256545f329.elb.us-east-1.amazonaws.com:7860"

async def proxy_handler(request):
    """Forward HTTP requests to NLB"""

    # Build target URL
    target_url = f"{NLB_VOICE_BOT}{request.path_qs}"

    logger.info(f"Proxying {request.method} {request.path} -> {target_url}")

    # Forward request
    async with aiohttp.ClientSession() as session:
        try:
            async with session.request(
                method=request.method,
                url=target_url,
                headers={k: v for k, v in request.headers.items()
                        if k.lower() not in ['host', 'content-length']},
                data=await request.read(),
                allow_redirects=False,
            ) as resp:

                # Copy response
                headers = {k: v for k, v in resp.headers.items()
                          if k.lower() not in ['content-encoding', 'transfer-encoding']}

                body = await resp.read()

                return web.Response(
                    status=resp.status,
                    headers=headers,
                    body=body
                )

        except Exception as e:
            logger.error(f"Proxy error: {e}")
            return web.Response(status=502, text=f"Bad Gateway: {e}")

async def websocket_handler(request):
    """Forward WebSocket connections to NLB"""

    logger.info(f"WebSocket connection to /ws")

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Connect to backend WebSocket
    target_url = f"ws://vpbank-voice-agent-nlb-b65730256545f329.elb.us-east-1.amazonaws.com:7860/ws"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(target_url) as backend_ws:

                # Bidirectional forwarding
                async def forward_to_backend():
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            await backend_ws.send_str(msg.data)
                        elif msg.type == aiohttp.WSMsgType.BINARY:
                            await backend_ws.send_bytes(msg.data)
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            break

                async def forward_to_client():
                    async for msg in backend_ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            await ws.send_str(msg.data)
                        elif msg.type == aiohttp.WSMsgType.BINARY:
                            await ws.send_bytes(msg.data)
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            break

                import asyncio
                await asyncio.gather(
                    forward_to_backend(),
                    forward_to_client(),
                )

    except Exception as e:
        logger.error(f"WebSocket proxy error: {e}")

    return ws

# Create app
app = web.Application()
app.router.add_route('*', '/ws', websocket_handler)
app.router.add_route('*', '/{tail:.*}', proxy_handler)

if __name__ == '__main__':
    logger.info("🔄 Starting HTTP Proxy to NLB...")
    logger.info(f"   Proxying to: {NLB_VOICE_BOT}")
    logger.info(f"   Listening on: 0.0.0.0:9090")

    web.run_app(app, host='0.0.0.0', port=9090)
