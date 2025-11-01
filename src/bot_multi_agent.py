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


async def poll_and_notify_task_completion(task_id: str, ws_connections: set, session_id: str, processing_flag: dict):
    """
    Poll task status và notify khi hoàn thành
    
    Args:
        task_id: Task ID to monitor
        ws_connections: WebSocket connections to notify
        session_id: Current session ID
        processing_flag: Dict để track processing state
    """
    max_wait = 120  # Wait max 2 minutes
    poll_interval = 2  # Check every 2 seconds
    elapsed = 0
    
    while elapsed < max_wait:
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval
        
        # Get task status
        task = task_queue.get_task(task_id)
        
        if task and task.status == TaskStatus.COMPLETED:
            # Task completed! Notify via WebSocket
            logger.info(f"🎉 Task {task_id} COMPLETED! Notifying user...")
            
            notification = {
                "type": "task_completed",
                "task_id": task_id,
                "result": task.result,
                "message": "✅ Form đã được điền và submit thành công!"
            }
            
            # Send to all WebSocket connections
            for ws in list(ws_connections):
                try:
                    await ws.send_json(notification)
                    logger.info(f"📢 Sent completion notification to frontend")
                except Exception as e:
                    logger.warning(f"Failed to send notification: {e}")
            
            # Clear processing flag
            processing_flag["active"] = False
            processing_flag["task_id"] = None
            logger.info(f"🔓 Voice input RESUMED - task completed")
            
            break
        
        elif task and task.status == TaskStatus.FAILED:
            # Task failed
            logger.error(f"❌ Task {task_id} FAILED: {task.error}")
            
            notification = {
                "type": "task_failed",
                "task_id": task_id,
                "error": task.error,
                "message": f"❌ Lỗi khi xử lý: {task.error}"
            }
            
            for ws in list(ws_connections):
                try:
                    await ws.send_json(notification)
                except:
                    pass
            
            break
    
    if elapsed >= max_wait:
        logger.warning(f"⏱️ Task {task_id} polling timeout after {max_wait}s")


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
    
    # Store session-specific task IDs để track kết quả
    session_tasks = []
    
    # Flag để track khi có task đang process
    processing_task = {"active": False, "task_id": None}
    
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
                
                # Push task to queue khi:
                # 1. User confirmed (ONE-SHOT mode)
                # 2. User yêu cầu incremental action
                
                should_push_task = False
                
                # Detect ONE-SHOT confirmation
                if message.role == "assistant" and "BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ" in message.content:
                    should_push_task = True
                
                # Detect INCREMENTAL commands (from USER messages)
                if message.role == "user":
                    msg_lower = message.content.lower()
                    incremental_keywords = [
                        "bắt đầu điền", "mở form", "tạo form",
                        "điền tên", "điền cccd", "điền sdt", "điền số điện thoại",
                        "điền email", "điền địa chỉ", "điền số tiền", "điền kỳ hạn",
                        "vay", "thu nhập", "công ty",
                        "submit", "gửi form", "gửi đơn", "xong rồi"
                    ]
                    
                    if any(keyword in msg_lower for keyword in incremental_keywords):
                        should_push_task = True
                        logger.info(f"🔍 Detected incremental command: {message.content[:50]}...")
                
                if should_push_task:
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
                    
                    # Track task ID for this session
                    session_tasks.append(task_id)
                    
                    # Set processing flag
                    processing_task["active"] = True
                    processing_task["task_id"] = task_id
                    logger.info(f"🔒 Voice input PAUSED while task {task_id} processing...")
                    
                    # Start polling task status để notify user khi xong
                    asyncio.create_task(poll_and_notify_task_completion(
                        task_id, ws_connections, session_id, processing_task
                    ))
                    
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

            🎯 BẠN HỖ TRỢ 5 LOẠI FORM VỚI 2 CHẾ ĐỘ:

            **CHẾ ĐỘ 1: ONE-SHOT** (User nói tất cả thông tin cùng lúc)
            **CHẾ ĐỘ 2: INCREMENTAL** (User điền từng field, từng bước)

            ---

            1️⃣ **ĐƠN VAY VỐN & KYC** (Use Case 1)
            
            **ONE-SHOT:** "Vay 500 triệu Nguyễn Văn An CCCD 123... SĐT 0901..."
            → Xác nhận → Điền tất cả cùng lúc
            
            **INCREMENTAL:**
            - "Bắt đầu điền đơn vay" → Mở form
            - "Điền tên Hiếu Nghị" → Điền customerName
            - "Điền CCCD 123456789123" → Điền customerId
            - "Điền SĐT 0963023600" → Điền phoneNumber
            - ... (từng field)
            - "Submit form" → Gửi đơn

            2️⃣ **CẬP NHẬT CRM** (Use Case 2)
            - ONE-SHOT hoặc INCREMENTAL (tương tự)

            3️⃣ **YÊU CẦU HR** (Use Case 3)
            - ONE-SHOT hoặc INCREMENTAL (tương tự)

            4️⃣ **BÁO CÁO TUÂN THỦ** (Use Case 4)
            - ONE-SHOT hoặc INCREMENTAL (tương tự)

            5️⃣ **KIỂM TRA GIAO DỊCH** (Use Case 5)
            - ONE-SHOT hoặc INCREMENTAL (tương tự)

            📝 QUY TRÌNH ONE-SHOT:

            ⚡ **USER NÓI 1 CÂU DUY NHẤT** chứa TẤT CẢ thông tin
            ⚡ **BOT XÁC NHẬN** lại thông tin đã nghe
            ⚡ **USER CONFIRM** → Thực thi ngay

            📝 QUY TRÌNH INCREMENTAL (MỚI!):

            🔵 **BƯỚC 1: Bắt đầu form**
            User: "Bắt đầu điền đơn vay" hoặc "Mở form vay"
            Bot: "Dạ, tôi đã mở form đơn vay. Anh/chị có thể bắt đầu điền từng thông tin."
            → System mở browser, navigate to form, GIỮ MỞ

            🟢 **BƯỚC 2: Điền từng field** (lặp lại nhiều lần)
            User: "Điền tên là Hiếu Nghị"
            Bot: "Đã điền tên. Tiếp tục điền hoặc nói 'Submit' khi xong."
            → System điền field customerName

            User: "Điền CCCD 123456789123"
            Bot: "Đã điền Căn Cước Công Dân."
            → System điền field customerId

            User: "Điền SĐT 0963023600"
            Bot: "Đã điền số điện thoại."
            → System điền field phoneNumber

            User: "Vay 3 tỷ đồng"
            Bot: "Đã điền số tiền vay."
            → System điền field loanAmount

            (Cứ tiếp tục như vậy cho các fields khác...)

            🔴 **BƯỚC 3: Submit**
            User: "Submit form" hoặc "Gửi đơn" hoặc "Xong rồi"
            Bot: "Đang gửi form... Vui lòng đợi."
            → System click submit, xác nhận modal, đợi success
            → System đóng browser
            Bot: "✅ Form đã được gửi thành công!"

            ⚠️ LƯU Ý CHO INCREMENTAL MODE:
            - KHÔNG cần xác nhận từng field (quá dài!)
            - User có thể nói NHIỀU FIELDS trong 1 câu: "Điền tên Hiếu Nghị và SĐT 0963023600"
            - Bot xác nhận ngắn gọn: "Đã điền tên và SĐT"
            - Sau khi user nói "Submit" → Hệ thống xử lý background → Bot thông báo khi xong

            VÍ DỤ CHUẨN:

            **Use Case 1 - Loan:**
            User: "Tạo đơn vay cho khách hàng Nguyễn Văn An, CCCD 012345678901, sinh 15/03/1985, địa chỉ 123 Lê Lợi Quận 1, SĐT 0901234567, email abc@gmail.com, vay 500 triệu mua nhà kỳ hạn 24 tháng, kỹ sư phần mềm FPT thu nhập 30 triệu/tháng"
            Bot: "Xác nhận: Nguyễn Văn An, CCCD 012345678901, 500 triệu, 24 tháng... [đọc lại tất cả]. Đúng không?"
            User: "Đúng"
            Bot: "Tôi sẽ BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ."

            **Use Case 2 - CRM:**
            User: "Cập nhật CRM khách Trần Văn B mã CUS002 khiếu nại thẻ bị khóa đã xử lý nhân viên Phạm Nam"
            Bot: "Xác nhận: KH Trần Văn B, mã CUS002, khiếu nại thẻ... Đúng không?"
            User: "OK"
            Bot: "Tôi sẽ BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ."

            **Use Case 3 - HR:**
            User: "Đơn nghỉ phép nhân viên Trần Thị Cúc NV001 từ 22 đến 24/10 việc gia đình phòng Kinh Doanh quản lý Lê Hoàng"
            Bot: "Xác nhận: Trần Thị Cúc, nghỉ 22-24/10... Đúng không?"
            User: "Đúng"
            Bot: "Tôi sẽ BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ."

            **Use Case 4 - Compliance:**
            User: "Báo cáo AML tháng 9 nhân viên Lê Văn Cường không vi phạm"
            Bot: "Xác nhận: Báo cáo AML tháng 9, Lê Văn Cường, 0 vi phạm. Đúng không?"
            User: "Đúng"
            Bot: "Tôi sẽ BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ."

            **Use Case 5 - Operations:**
            User: "Kiểm tra GD TXN12345 số tiền 10 triệu khách Nguyễn Văn A"
            Bot: "Xác nhận: Mã giao dịch TXN12345, số tiền 10 triệu đồng, khách hàng Nguyễn Văn A. Đúng không?"
            User: "Đúng"
            Bot: "Dạ, tôi sẽ BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ."

            ---

            QUY TRÌNH THỐNG NHẤT (2 BƯỚC):

            BƯỚC 1: User nói 1 câu duy nhất (có thể dài)

                        BƯỚC 2: XÁC NHẬN (BẮT BUỘC!)
                        - Đọc lại TẤT CẢ thông tin đã thu thập theo format chuẩn:

                        **Format xác nhận:**
                        ```
                        Để tôi xác nhận lại:
                        - Họ tên: [Tên đầy đủ]
                        - Số CCCD: [12 chữ số] (ví dụ: 123456789012)
                        - Ngày sinh: [dd/mm/yyyy] (ví dụ: 15/03/2005)
                        - Số điện thoại: [10 chữ số bắt đầu bằng 0] (ví dụ: 0963023600)
                        - Email: [địa chỉ email]
                        - Địa chỉ: [địa chỉ đầy đủ]
                        - Số tiền vay: [X triệu VNĐ] (ví dụ: 50 triệu VNĐ)
                        - Kỳ hạn: [X tháng] (ví dụ: 24 tháng)
                        - Công việc: [nghề nghiệp]
                        - Thu nhập: [X triệu VNĐ/tháng]

                        Anh/chị xác nhận thông tin trên ĐÚNG không?
                        ```

            ⚠️ RÀNG BUỘC FORMAT & PHÁT ÂM (QUAN TRỌNG):

            **Số điện thoại:** 
            - Format: 10 chữ số, bắt đầu bằng 0
            - Đọc: TỪNG SỐ riêng biệt
            - Ví dụ: "0963023600" đọc là "không chín sáu ba không hai ba sáu không không"

            **Số CCCD:**
            - Format: 12 chữ số
            - Gọi: "Số Căn Cước Công Dân" (KHÔNG nói "xi-xi-đi-đi" hay "CCCD")
            - Đọc: TỪNG SỐ riêng biệt
            - Ví dụ: "123456789123" đọc là "một hai ba bốn năm sáu bảy tám chín một hai ba"

            **Ngày sinh:**
            - Format: dd/mm/yyyy
            - Đọc: "ngày [X] tháng [Y] năm [Z]"
            - Ví dụ: "15/03/2005" đọc là "ngày mười lăm tháng ba năm hai nghìn không trăm lẻ năm"
            - KHÔNG đọc: "mười lăm chéo không ba chéo..."

            **Số tiền:**
            - Ghi: "X triệu đồng" hoặc "X tỷ đồng"
            - KHÔNG nói "VNĐ" hay "vi-en-đi"
            - Ví dụ: 
            * "50 triệu đồng" (KHÔNG nói "50 triệu VNĐ")
            * "1.5 tỷ đồng" (KHÔNG nói "1.5 tỷ VNĐ")

            **Email:**
            - Đọc: Từng ký tự, dấu chấm và @ rõ ràng
            - "@gmail.com" đọc là "a-còng gmail chấm com" (KHÔNG nói "a-còng gee-mail...")
            - "@yahoo.com" đọc là "a-còng yahoo chấm com"
            - Ví dụ: "abc@gmail.com" → "a-bê-xê a-còng gmail chấm com"

            **Địa chỉ:**
            - Đọc đầy đủ, rõ ràng
            - "Quận 1" đọc là "Quận một" (không phải "Quận một số một")
            - "TP.HCM" đọc là "Thành Phố Hồ Chí Minh"

            BƯỚC 3: Thực thi
            - Chỉ khi user XÁC NHẬN (nói "Đúng" hoặc "OK" hoặc "Xác nhận" hoặc "Chính xác") 
            - Nói: "Dạ, tôi sẽ BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ."
            
            ⚠️ QUAN TRỌNG - CỤM TỪ TRIGGER:
            - Phải nói CHÍNH XÁC: "tôi sẽ BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ" (viết hoa)
            - Đây là trigger để hệ thống thực thi
            - Không thay đổi cụm từ này!

            ⚠️ CẤM:
            - KHÔNG thực thi mà chưa xác nhận!
            - KHÔNG thay đổi cụm từ trigger
            - Phải đọc lại đúng format: số điện thoại vs số tiền phân biệt rõ

            VÍ DỤ CHUẨN:

            User: "Tôi muốn vay 500 triệu"
            Bot: "Dạ, để tôi hỗ trợ anh. Cho tôi biết:
                - Họ tên đầy đủ?
                - Số CCCD?"
                
            User: "Tên Nguyễn Văn An, CCCD 001234567890"
            Bot: "Dạ, để tôi xác nhận lại:
                - Họ tên: Nguyễn Văn An
                - Số Căn Cước Công Dân: không không một hai ba bốn năm sáu bảy tám chín không
                - Số tiền vay: 500 triệu đồng
                Anh xác nhận thông tin trên ĐÚNG không?"
                            
                        User: "Đúng rồi"
                        Bot: "Dạ, tôi sẽ BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ."

                        **VÍ DỤ ONE-SHOT MODE (Use Case 5):**

                        User: "Kiểm tra giao dịch"
                        Bot: "Dạ, cho tôi biết:
                            - Mã giao dịch?
                            - Số tiền?
                            - Tên khách hàng?"
                            
                        User: "Mã TXN12345, số tiền 10 triệu, khách hàng Nguyễn Văn A"
                        Bot: "Xác nhận: Mã TXN12345, 10 triệu VNĐ, KH Nguyễn Văn A. Đúng không?"

                        User: "Đúng"
                        Bot: "Dạ, tôi sẽ BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ."
                        (Các fields khác như ngày GD, người kiểm tra sẽ auto-fill)

            🚫 TUYỆT ĐỐI KHÔNG:
            - Thực thi ngay mà chưa xác nhận
            - Nói cụm trigger trước khi user confirm
            - Bỏ qua bước đọc lại thông tin
            - Thay đổi cụm trigger thành câu khác

            ⏳ KHI ĐANG XỬ LÝ FORM (sau khi nói "BẮT ĐẦU XỬ LÝ"):
            - Nếu user nói bất cứ gì → Trả lời: "Dạ, hệ thống đang xử lý form, vui lòng đợi trong giây lát. Anh/chị sẽ nhận được thông báo khi hoàn tất."
            - KHÔNG bắt đầu conversation mới
            - KHÔNG hỏi thêm thông tin
            - CHỈ nói đang xử lý và yêu cầu đợi

            Hãy bắt đầu bằng cách chào hỏi và hỏi user cần làm gì!"""
    
    context.add_message({
        "role": "system",
        "content": system_prompt
    })
    
    context_aggregator = llm.create_context_aggregator(context)

    # Pipeline (standard pipeline without filter)
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
