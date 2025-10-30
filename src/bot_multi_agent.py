"""
Bot Multi-Agent - VPBank Form Automation
Tích hợp multi-agent workflow vào pipeline hiện tại
"""
import asyncio
import os
import json
import uuid
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

# Import task queue and worker
from .task_queue import task_queue, Task, TaskType
from .workflow_worker import workflow_worker, create_worker_task

load_dotenv(override=True)

# Environment variables
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")
openai_api_key = os.getenv("OPENAI_API_KEY")

routes = RouteTableDef()

# WebSocket connections cho transcript streaming
ws_connections = set()

# ICE servers
ice_servers = [
    IceServer(urls="stun:stun.l.google.com:19302"),
    IceServer(
        urls="turn:openrelay.metered.ca:80",
        username="openrelayproject",
        credential="openrelayproject"
    ),
]


async def push_task_to_queue(user_message: str, session_id: str) -> str:
    """
    Push task to queue for background processing
    
    Args:
        user_message: User's voice input
        session_id: Current session ID
        
    Returns:
        task_id: Unique task identifier
    """
    # Detect task type from message (simple keyword matching)
    task_type = TaskType.LOAN  # Default
    
    msg_lower = user_message.lower()
    if any(keyword in msg_lower for keyword in ["vay", "khoản vay", "kyc", "cccd"]):
        task_type = TaskType.LOAN
    elif any(keyword in msg_lower for keyword in ["crm", "khách hàng", "cập nhật", "thông tin"]):
        task_type = TaskType.CRM
    elif any(keyword in msg_lower for keyword in ["hr", "nhân sự", "nghỉ phép", "đào tạo"]):
        task_type = TaskType.HR
    elif any(keyword in msg_lower for keyword in ["compliance", "tuân thủ", "báo cáo", "aml"]):
        task_type = TaskType.COMPLIANCE
    elif any(keyword in msg_lower for keyword in ["operations", "giao dịch", "đối soát", "kiểm tra"]):
        task_type = TaskType.OPERATIONS
    
    # Create task
    task = Task(
        task_type=task_type,
        user_message=user_message,
        extracted_data={"session_id": session_id}
    )
    
    # Push to queue
    task_id = await task_queue.push(task)
    
    return task_id


async def run_bot(webrtc_connection, ws_connections):
    """
    Run bot with multi-agent workflow
    """
    logger.info("🚀 Starting bot with multi-agent system...")
    
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

    tts = OpenAITTSService(
        api_key=openai_api_key,
        voice="nova",
        model="gpt-4o-mini-tts"
    )
    
    # Start workflow worker in background (processes tasks from queue)
    logger.info("🔨 Starting workflow worker...")
    worker_task = create_worker_task()
    logger.info("✅ Workflow worker started in background!")

    # Transcript processor
    transcript = TranscriptProcessor()
    
    # Create session
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    transcript_file = f"transcripts/conversation_{session_id}.json"
    os.makedirs("transcripts", exist_ok=True)
    
    transcript_data = {
        "session_id": session_id,
        "started_at": datetime.now().isoformat(),
        "messages": [],
        "workflow_executions": []
    }
    
    # Transcript handler
    @transcript.event_handler("on_transcript_update")
    async def handle_transcript_update(processor, frame):
        """Handle transcript updates"""
        try:
            for message in frame.messages:
                msg_dict = {
                    "role": message.role,
                    "content": message.content,
                    "timestamp": message.timestamp or datetime.now().isoformat()
                }
                transcript_data["messages"].append(msg_dict)
                
                # Save to file
                with open(transcript_file, 'w', encoding='utf-8') as f:
                    json.dump(transcript_data, f, ensure_ascii=False, indent=2)
                
                # Send to WebSocket clients
                for ws in list(ws_connections):
                    try:
                        await ws.send_json({
                            "type": "transcript",
                            "message": msg_dict
                        })
                    except Exception as e:
                        logger.warning(f"Failed to send transcript: {e}")
                        ws_connections.discard(ws)
                
                # Push task to queue CHỈ KHI user đã CONFIRM
                # Detect confirmation keyword từ assistant message
                if message.role == "assistant" and "[CONFIRM_AND_EXECUTE]" in message.content:
                    # Lấy TOÀN BỘ conversation history để extract thông tin
                    all_messages = transcript_data["messages"]
                    
                    # Format: "role: content" for each message
                    conversation_history = []
                    for m in all_messages:
                        conversation_history.append(f"{m['role']}: {m['content']}")
                    
                    # Join tất cả messages
                    full_context = "\n".join(conversation_history)
                    
                    task_id = await push_task_to_queue(full_context, session_id)
                    logger.info(f"✅ User CONFIRMED! Task {task_id} pushed to queue")
                    logger.debug(f"   Full context ({len(all_messages)} messages) sent to workflow")
                    
                logger.info(f"📝 [{message.role}]: {message.content}")
        except Exception as e:
            logger.error(f"Error handling transcript: {e}")

    # Create WebRTC transport
    transport = SmallWebRTCTransport(
        webrtc_connection=webrtc_connection,
        params=TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(
                params=VADParams(
                    stop_secs=2,
                    start_secs=0.1,
                    min_volume=0.6
                )
            ),
        ),
    )

    # Create context with system prompt
    context = OpenAILLMContext()
    
    # System prompt cho Voice Agent
    system_prompt = """Bạn là trợ lý ảo thông minh của VPBank, chuyên hỗ trợ điền form tự động qua giọng nói.

🎯 BẠN HỖ TRỢ 5 LOẠI FORM:

1️⃣ **ĐƠN VAY VỐN & KYC** (Use Case 1)
   - Từ khóa: "vay", "khoản vay", "đơn vay", "KYC", "CCCD"
   - Thông tin cần: Họ tên, CCCD, ngày sinh, địa chỉ, SĐT, email, số tiền vay, kỳ hạn, mục đích vay, công việc, thu nhập

2️⃣ **CẬP NHẬT CRM** (Use Case 2)
   - Từ khóa: "CRM", "cập nhật khách hàng", "thông tin khách hàng"
   - Thông tin cần: Tên KH, mã KH, loại tương tác, ngày tương tác, vấn đề, giải pháp, nhân viên xử lý

3️⃣ **YÊU CẦU HR** (Use Case 3)
   - Từ khóa: "HR", "nghỉ phép", "đào tạo", "nhân viên"
   - Thông tin cần: Tên NV, mã NV, loại yêu cầu, ngày bắt đầu, ngày kết thúc, lý do

4️⃣ **BÁO CÁO TUÂN THỦ** (Use Case 4)
   - Từ khóa: "compliance", "tuân thủ", "báo cáo", "AML"
   - Thông tin cần: Loại báo cáo, kỳ báo cáo, người nộp, số vi phạm, mức độ rủi ro

5️⃣ **KIỂM TRA GIAO DỊCH** (Use Case 5)
   - Từ khóa: "giao dịch", "transaction", "đối soát", "kiểm tra"
   - Thông tin cần: Mã GD, ngày GD, tên KH, số tiền, loại GD, người thụ hưởng

📝 QUY TRÌNH BẮT BUỘC (3 BƯỚC):

BƯỚC 1: Thu thập thông tin
- Hỏi từng thông tin cần thiết
- Ghi nhận đầy đủ

BƯỚC 2: XÁC NHẬN LẠI (BẮT BUỘC!)
- Đọc lại TẤT CẢ thông tin đã thu thập
- Hỏi: "Anh/chị xác nhận thông tin trên ĐÚNG không?"
- Chờ user trả lời: "Đúng", "OK", "Xác nhận", "Được"

BƯỚC 3: Thực thi
- Chỉ khi user XÁC NHẬN → Nói: "Tôi sẽ thực hiện điền form ngay."
- KẾT THÚC câu bằng từ khóa: **"[CONFIRM_AND_EXECUTE]"**

⚠️ QUAN TRỌNG:
- KHÔNG BAO GIỜ thực thi mà chưa xác nhận!
- Phải ĐỌC LẠI tất cả thông tin trước khi hỏi xác nhận
- Chỉ thêm [CONFIRM_AND_EXECUTE] khi user đã nói: "Đúng/OK/Xác nhận"

VÍ DỤ CHUẨN:

User: "Tôi muốn vay 500 triệu"
Bot: "Dạ, để tôi hỗ trợ anh. Cho tôi biết:
      - Họ tên đầy đủ?
      - Số CCCD?"
      
User: "Tên Nguyễn Văn An, CCCD 001234567890"
Bot: "Dạ, để tôi xác nhận lại:
      - Họ tên: Nguyễn Văn An
      - CCCD: 001234567890
      - Số tiền vay: 500 triệu VNĐ
      Anh xác nhận thông tin trên ĐÚNG không?"
      
User: "Đúng rồi"
Bot: "Dạ, tôi sẽ thực hiện điền form đơn vay ngay. [CONFIRM_AND_EXECUTE]"

🚫 TUYỆT ĐỐI KHÔNG:
- Thực thi ngay mà chưa xác nhận
- Thêm [CONFIRM_AND_EXECUTE] trước khi user confirm
- Bỏ qua bước đọc lại thông tin

Hãy bắt đầu bằng cách chào hỏi và hỏi user cần làm gì!"""
    
    context.add_message({
        "role": "system",
        "content": system_prompt
    })
    
    context_aggregator = llm.create_context_aggregator(context)

    # Pipeline (giữ nguyên cấu trúc cũ để tương thích)
    pipeline = Pipeline([
        transport.input(),
        stt,
        transcript.user(),
        context_aggregator.user(),
        llm,
        tts,
        transport.output(),
        transcript.assistant(),
        context_aggregator.assistant(),
    ])

    # Create task
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

    # Run pipeline
    runner = PipelineRunner()
    await runner.run(task)
    
    # Save final transcript
    transcript_data["ended_at"] = datetime.now().isoformat()
    with open(transcript_file, 'w', encoding='utf-8') as f:
        json.dump(transcript_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"💾 Session completed. Transcript saved to {transcript_file}")



@routes.post("/offer")
async def handle_offer(request):
    """Handle WebRTC offer"""
    try:
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        
        body = await request.json()
        offer_sdp = body.get("sdp")
        offer_type = body.get("type")
        
        if not offer_sdp or offer_type != "offer":
            return web.json_response(
                {"error": "Invalid offer"},
                status=400,
                headers=headers
            )
        
        # Create WebRTC connection
        logger.info("🔧 Creating WebRTC connection...")
        webrtc_connection = SmallWebRTCConnection(ice_servers=ice_servers)
        
        # Initialize connection with offer (NEW API in pipecat 0.0.91)
        logger.info("🔧 Initializing WebRTC connection with offer...")
        await webrtc_connection.initialize(
            sdp=offer_sdp,
            type=offer_type
        )
        
        # Get answer from connection (NEW API)
        logger.info("🔧 Getting answer from WebRTC connection...")
        answer = webrtc_connection.get_answer()
        logger.info(f"✅ Got answer")
        
        # Start bot pipeline
        logger.info("🚀 Starting bot pipeline...")
        asyncio.create_task(run_bot(webrtc_connection, ws_connections))
        
        logger.info("✅ Bot pipeline started successfully")
        return web.json_response(answer, headers=headers)
        
    except Exception as e:
        logger.error(f"Error handling offer: {e}")
        return web.json_response(
            {"error": str(e)},
            status=500
        )


@routes.options("/offer")
async def handle_offer_options(request):
    """Handle CORS preflight"""
    return web.Response(
        headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
    )


@routes.get("/ws")
async def websocket_handler(request):
    """WebSocket for transcript streaming"""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    ws_connections.add(ws)
    logger.info(f"📡 WebSocket connected. Total connections: {len(ws_connections)}")
    
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                logger.debug(f"Received WS message: {msg.data}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        ws_connections.discard(ws)
        logger.info(f"📡 WebSocket disconnected. Remaining: {len(ws_connections)}")
    
    return ws


def create_app():
    """Create aiohttp application"""
    app = web.Application()
    app.add_routes(routes)
    
    # CORS middleware
    async def cors_middleware(app, handler):
        async def middleware(request):
            if request.method == "OPTIONS":
                return web.Response(
                    headers={
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type',
                    }
                )
            response = await handler(request)
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        return middleware
    
    app.middlewares.append(cors_middleware)
    
    return app


if __name__ == "__main__":
    logger.info("🚀 Starting VPBank Multi-Agent Bot Server...")
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=7860)
