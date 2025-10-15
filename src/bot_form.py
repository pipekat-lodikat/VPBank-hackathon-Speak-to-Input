# bot_form.py - Google Sheets voice filling bot based on original debt collection bot

import asyncio
import os
import json
from datetime import datetime
from aiohttp import web
from aiohttp.web import RouteTableDef
from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer, VADParams
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.pipeline.runner import PipelineRunner
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport
from pipecat.transports.smallwebrtc.connection import SmallWebRTCConnection, IceServer
from pipecat.transports.base_transport import TransportParams
from pipecat.services.aws.stt import AWSTranscribeSTTService
from pipecat.services.aws.llm import AWSBedrockLLMService
from pipecat.services.openai.tts import OpenAITTSService
from pipecat.transcriptions.language import Language
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.transcript_processor import TranscriptProcessor
from pipecat_flows import FlowManager
from flow_form import create_sheet_filling_node
from browser_agent import browser_agent

load_dotenv(override=True)

# Set biến môi trường
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")
openai_api_key = os.getenv("OPENAI_API_KEY") 


# Google Sheets URL - Change this to your sheet URL
GOOGLE_SHEETS_URL = os.getenv("GOOGLE_SHEETS_URL", "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit")

routes = RouteTableDef()

# Set kết nối WebSocket để truyền backend transcript -> frontend React
ws_connections = set()

# ICE servers for NAT traversal
# Add TURN server for Docker/container environments to avoid random UDP ports
ice_servers = [
    IceServer(urls="stun:stun.l.google.com:19302"),
    # Option 1: Use free TURN server (limited, for testing only)
    # IceServer(
    #     urls="turn:openrelay.metered.ca:80",
    #     username="openrelayproject",
    #     credential="openrelayproject"
    # ),
    # Option 2: Use your own TURN server (recommended for production)
    # IceServer(
    #     urls="turn:your-turn-server.com:3478",
    #     username=os.getenv("TURN_USERNAME"),
    #     credential=os.getenv("TURN_PASSWORD")
    # ),
]

async def run_bot(webrtc_connection, ws_connections):
    """Run the bot pipeline with the given WebRTC connection."""
    # Initialize services
    stt = AWSTranscribeSTTService(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_region=aws_region,
        language=Language.VI
    )

    llm = AWSBedrockLLMService(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_region=aws_region,
        model=os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
    )

    # Sử dụng Text-to-Speech của OpenAI thay vì ElevenLabs để debugging chi phí tiết kiệm  ~10 lần

    tts = OpenAITTSService(
        api_key=os.getenv("OPENAI_API_KEY"),
        voice="nova",
        model="gpt-4o-mini-tts" 
    )
    

    # Xử lý lịch sử cuộc trò chuyện
    transcript = TranscriptProcessor()
    
    # Tạo file cuộc trò chuyện mới với mốc thời gian
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    transcript_file = f"transcripts/conversation_{session_id}.json"
    os.makedirs("transcripts", exist_ok=True)
    
    # Khoi tạo dữ liệu cuộc trò chuyện 
    transcript_data = {
        "session_id": session_id,
        "started_at": datetime.now().isoformat(),
        "messages": []
    }
    
    # Lưu file lịch sử cuộc trò chuyện
    @transcript.event_handler("on_transcript_update")
    async def handle_transcript_update(processor, frame):
        """Handle transcript updates and save to file + send to UI."""
        try:
            for message in frame.messages:
                msg_dict = {
                    "role": message.role,
                    "content": message.content,
                    "timestamp": message.timestamp or datetime.now().isoformat()
                }
                transcript_data["messages"].append(msg_dict)
                with open(transcript_file, 'w', encoding='utf-8') as f:
                    json.dump(transcript_data, f, ensure_ascii=False, indent=2)
                
                if ws_connections:
                    logger.info(f"📡 Sending to {len(ws_connections)} WebSocket clients")
                for ws in list(ws_connections):
                    try:
                        await ws.send_json({
                            "type": "transcript",
                            "message": msg_dict
                        })
                        logger.debug(f"✅ Sent transcript to WebSocket client")
                    except Exception as e:
                        logger.warning(f"Failed to send transcript to WebSocket: {e}")
                        ws_connections.discard(ws)
                
                logger.info(f"📝 [{message.role}]: {message.content}")
        except Exception as e:
            logger.error(f"Error handling transcript update: {e}")

    # Tạo transport WebRTC
    transport = SmallWebRTCTransport(
        webrtc_connection=webrtc_connection,
        params=TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(
                params=VADParams(
                    stop_secs=0.7, # Thời gian dừng phát hiện giọng nói
                    start_secs=0.1, # Thời gian bắt đầu phát hiện giọng nói
                    min_volume=0.6 # Giảm ngưỡng âm lượng để nhận giọng nói nhỏ hơn
                )
            ),
        ),
    )

    # Tạo ngữ cảnh (memory) cũng như phương thức tổng hợp context cho LLM
    context = OpenAILLMContext()
    context_aggregator = llm.create_context_aggregator(context)

    # Pipeline xử lý chính (without flow_manager first)
    pipeline = Pipeline([
        transport.input(),
        stt,
        transcript.user(),               # Nhận transcript người dùng
        context_aggregator.user(),      # Tạo LLMMessagesFrame
        llm,                            # Nhận LLMMessagesFrame và tạo phản hồi
        tts,
        transport.output(),
        transcript.assistant(),          # Nhận transcript bot
        context_aggregator.assistant(),
    ])

    # Tạo PipelineTask với các tham số cần thiết (Lớp để quản lý pipeline)
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            enable_vad=True,
            vad_analyzer=SileroVADAnalyzer(
                params=VADParams(
                    stop_secs=0.7,
                    start_secs=0.1,
                    min_volume=0.6
                )
            ),
        ),
    )

    # Tạo FlowManager với task đã có giá trị
    flow_manager = FlowManager(
        task=task,
        llm=llm,
        context_aggregator=context_aggregator,
        transport=transport,
        tts=tts
    )

    # Khởi tạo flow và node ban đầu cho sheet filling
    await flow_manager.initialize()
    await flow_manager.set_node("initial_node", create_sheet_filling_node())

    # Browser will be initialized lazily when first needed
    # No eager initialization - saves resources
    logger.info("🌐 Browser agent ready (lazy init - will start on first use)")

    # Use PipelineRunner to run the task
    runner = PipelineRunner()
    await runner.run(task)
    
    # Kết thúc cuộc trò chuyện và lưu file lịch sử cuộc trò chuyện
    transcript_data["ended_at"] = datetime.now().isoformat()
    with open(transcript_file, 'w', encoding='utf-8') as f:
        json.dump(transcript_data, f, ensure_ascii=False, indent=2)
    logger.info(f"💾 Transcript saved to {transcript_file}")

    # Cleanup browser if it was initialized
    try:
        if browser_agent._initialized:
            await browser_agent.close()
            logger.info("🔒 Browser closed successfully")
    except Exception as e:
        logger.error(f"Failed to close browser agent: {e}")

@routes.post("/offer")
async def handle_offer(request):
    """Handle WebRTC offer from client."""
    try:
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        
        logger.info(f"📞 Request method: {request.method}")
        logger.info(f"📞 Request headers: {dict(request.headers)}")
        logger.info(f"📞 Content-Length: {request.content_length}")
        logger.info(f"📞 Content-Type: {request.content_type}")

        try:
            body = await request.text()
            logger.info(f"📞 Body length: {len(body)}")
            logger.info(f"📞 Body content: {body}")
            
            if not body or not body.strip():
                # Maybe it's raw bytes?
                raw_body = await request.read()
                logger.info(f"📞 Raw body length: {len(raw_body)}")
                logger.info(f"📞 Raw body: {raw_body}")

                if not raw_body:
                    logger.error("📞 Both text and raw body are empty")
                    return web.json_response(
                        {"error": "Request body is empty"}, 
                        status=400,
                        headers=headers
                    )
                
                # Try to decode raw body
                body = raw_body.decode('utf-8')
                logger.info(f"📞 Decoded body: {body}")

        except Exception as read_err:
            logger.error(f"Error reading request body: {read_err}")
            return web.json_response(
                {"error": f"Error reading request: {str(read_err)}"}, 
                status=400,
                headers=headers
            )
        
        # Parse JSON from the body text
        try:
            import json
            offer_data = json.loads(body)
            logger.info(f"✅ Successfully parsed JSON")
            logger.info(f"📋 Offer keys: {list(offer_data.keys())}")
            
        except json.JSONDecodeError as json_err:
            logger.error(f"❌ JSON parsing error: {json_err}")
            logger.error(f"Raw body for debug: {repr(body)}")
            return web.json_response(
                {"error": f"Invalid JSON: {str(json_err)}"}, 
                status=400,
                headers=headers
            )
        
        # Validate offer structure
        if "sdp" not in offer_data or "type" not in offer_data:
            logger.error(f"❌ Invalid offer structure. Got keys: {list(offer_data.keys())}")
            return web.json_response(
                {"error": "Invalid offer structure. Need 'sdp' and 'type' fields"}, 
                status=400,
                headers=headers
            )
        
        logger.info(f"✅ Received valid WebRTC offer")
        logger.info(f"📋 Offer type: {offer_data['type']}")
        logger.info(f"📋 SDP length: {len(offer_data['sdp'])}")
        
        # Tạo kết nối WebRTC - sử dụng API đúng như trong bot.py
        logger.info("🔧 Creating WebRTC connection...")
        webrtc_connection = SmallWebRTCConnection(ice_servers=ice_servers)
        
        # Initialize connection with offer - sử dụng API đúng
        logger.info("🔧 Initializing WebRTC connection with offer...")
        await webrtc_connection.initialize(
            sdp=offer_data["sdp"],
            type=offer_data["type"]
        )
        
        # Get answer from connection - sử dụng API đúng
        logger.info("🔧 Getting answer from WebRTC connection...")
        answer = webrtc_connection.get_answer()
        logger.info(f"✅ Got answer: {answer}")
        
        # Start the bot pipeline in background with WebSocket connections
        logger.info("🚀 Starting bot pipeline...")
        asyncio.create_task(run_bot(webrtc_connection, ws_connections))
        
        logger.info("✅ Bot pipeline started successfully")
        return web.json_response(answer, headers=headers)
        
    except Exception as e:
        logger.error(f"❌ Error handling offer: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return web.json_response(
            {"error": str(e)}, 
            status=500,
            headers={'Access-Control-Allow-Origin': '*'}
        )

@routes.options("/offer")
async def handle_offer_options(request):
    """Handle CORS preflight for /offer endpoint."""
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    return web.Response(headers=headers)

@routes.get("/ws")
async def websocket_handler(request):
    """Handle WebSocket connections for transcript streaming."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    # Add to active connections
    ws_connections.add(ws)
    logger.info(f"WebSocket client connected. Total connections: {len(ws_connections)}")
    
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                # Handle incoming messages from client if needed
                data = json.loads(msg.data)
                logger.debug(f"Received WebSocket message: {data}")
            elif msg.type == web.WSMsgType.ERROR:
                logger.error(f'WebSocket error: {ws.exception()}')
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Remove from active connections
        ws_connections.discard(ws)
        logger.info(f"WebSocket client disconnected. Total connections: {len(ws_connections)}")
    
    return ws

@routes.get("/")
async def index(request):
    """Simple index page."""
    return web.Response(
        text="VP Bank Sheets Filling Voice Agent is running! Use React UI to connect.",
        content_type="text/plain"
    )

def create_app():
    """Create the aiohttp application."""
    app = web.Application()
    
    # Add CORS middleware
    @web.middleware
    async def cors_middleware(request, handler):
        # Handle CORS preflight requests
        if request.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Max-Age': '86400',
            }
            return web.Response(headers=headers)
        
        # Handle actual requests
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    app.middlewares.append(cors_middleware)
    app.router.add_routes(routes)
    return app

async def main():
    """Main entry point."""
    logger.info("🚀 Starting VP Bank Sheets Filling Voice Agent...")
    
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', 7860)
    await site.start()
    
    logger.info("✅ Server started at http://localhost:7860")
    logger.info("📱 WebRTC endpoint: POST http://localhost:7860/offer")
    logger.info("📡 WebSocket endpoint: WS http://localhost:7860/ws")
    logger.info("🌐 React UI: http://localhost:5173")
    logger.info(f"📊 Google Sheets URL: {GOOGLE_SHEETS_URL}")
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("👋 Shutting down server...")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
