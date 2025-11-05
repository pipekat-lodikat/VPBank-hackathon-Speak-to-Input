"""
Voice Bot - VPBank Form Automation
Voice interface với WebRTC, STT, TTS, và LLM
Gửi requests đến Browser Agent Service để thực hiện automation
"""
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
from pipecat.services.elevenlabs import ElevenLabsTTSService
from pipecat.transcriptions.language import Language
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.transcript_processor import TranscriptProcessor

# Browser Agent Service URL
BROWSER_SERVICE_URL = os.getenv("BROWSER_SERVICE_URL", "http://localhost:7863")

load_dotenv(override=True)

# Environment variables
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")
openai_api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID")

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


async def push_to_browser_service(user_message: str, ws_connections: set, session_id: str, processing_flag: dict):
    """
    Gửi request đến Browser Agent Service qua HTTP API
    
    Args:
        user_message: Full conversation context từ user
        ws_connections: WebSocket connections để notify
        session_id: Current session ID
        processing_flag: Dict để track processing state
    """
    import aiohttp
    
    try:
        logger.info(f"📤 Pushing request to Browser Service for session {session_id}")
        logger.debug(f"   Service URL: {BROWSER_SERVICE_URL}")
        logger.debug(f"   Message length: {len(user_message)} chars")
        
        # Prepare request
        payload = {
            "user_message": user_message,
            "session_id": session_id
        }
        
        # Send HTTP POST request
        timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{BROWSER_SERVICE_URL}/api/execute",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    if result.get("success"):
                        final_message = result.get("result", "Completed")
                        
                        # Filter JSON from response (avoid TTS reading JSON)
                        if isinstance(final_message, str):
                            # Remove JSON code blocks
                            import re
                            # Remove ```json blocks
                            final_message = re.sub(r'```json\s*\{[^}]*\}\s*```', '', final_message, flags=re.DOTALL)
                            # Remove ``` blocks
                            final_message = re.sub(r'```[^`]*```', '', final_message, flags=re.DOTALL)
                            # Remove { } blocks
                            final_message = re.sub(r'\{[^}]*\}', '', final_message)
                            # Clean up extra whitespace
                            final_message = final_message.strip()
                        
                        # If empty after filtering, use default message
                        if not final_message or len(final_message) < 5:
                            final_message = "Đã điền thành công"
                        
                        logger.info(f"✅ Browser Service completed! Result: {final_message[:200]}...")
                        
                        # Notify via WebSocket
                        notification = {
                            "type": "task_completed",
                            "result": final_message,
                            "message": f"✅ {final_message}"
                        }
                        
                        for ws in list(ws_connections):
                            try:
                                await ws.send_json(notification)
                                logger.info(f"📢 Sent completion notification to frontend")
                            except Exception as e:
                                logger.warning(f"Failed to send notification: {e}")
                    else:
                        error_msg = result.get("error", "Unknown error")
                        logger.error(f"❌ Browser Service failed: {error_msg}")
                        
                        notification = {
                            "type": "task_failed",
                            "error": error_msg,
                            "message": f"❌ Lỗi khi xử lý: {error_msg}"
                        }
                        
                        for ws in list(ws_connections):
                            try:
                                await ws.send_json(notification)
                            except:
                                pass
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Browser Service HTTP error {response.status}: {error_text}")
                    
                    notification = {
                        "type": "task_failed",
                        "error": f"HTTP {response.status}: {error_text}",
                        "message": f"❌ Lỗi kết nối với Browser Service"
                    }
                    
                    for ws in list(ws_connections):
                        try:
                            await ws.send_json(notification)
                        except:
                            pass
        
        # Clear processing flag
        processing_flag["active"] = False
        processing_flag["task_id"] = None
        logger.info(f"🔓 Voice input RESUMED")
        
    except asyncio.TimeoutError:
        logger.error(f"❌ Browser Service timeout after 5 minutes")
        
        notification = {
            "type": "task_failed",
            "error": "Timeout",
            "message": "❌ Browser Service không phản hồi (timeout)"
        }
        
        for ws in list(ws_connections):
            try:
                await ws.send_json(notification)
            except:
                pass
        
        processing_flag["active"] = False
        processing_flag["task_id"] = None
        
    except Exception as e:
        logger.error(f"❌ Error calling Browser Service: {e}", exc_info=True)
        
        notification = {
            "type": "task_failed",
            "error": str(e),
            "message": f"❌ Lỗi kết nối: {str(e)}"
        }
        
        for ws in list(ws_connections):
            try:
                await ws.send_json(notification)
            except:
                pass
        
        processing_flag["active"] = False
        processing_flag["task_id"] = None


async def run_bot(webrtc_connection, ws_connections):
    """
    Run bot with multi-agent workflow
    """
    logger.info("🚀 Starting voice bot...")
    
    # Flag để track khi có workflow đang process
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

    # Text-to-Speech - ElevenLabs TTS (thay cho OpenAI TTS)
    tts = ElevenLabsTTSService(
        api_key=elevenlabs_api_key,
        voice_id=elevenlabs_voice_id,
        model="eleven_flash_v2_5",
        params=ElevenLabsTTSService.InputParams(
            language=Language.VI,
            stability=0.8,
            similarity_boost=0.75,
            style=0,
            use_speaker_boost=True,
            speed=1.0
        )
    )
    
    logger.info("🚀 Voice bot ready - workflow will execute directly when needed")

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
                
                # Push ngay lập tức khi user nói về form filling (incremental mode)
                # Mỗi user message có thể là: tên, cccd, sdt, số tiền, etc. → push ngay để điền field đó
                
                should_push_task = False
                
                if message.role == "user":
                    msg_lower = message.content.lower()
                    
                    # Detect form filling intent - push ngay lập tức (incremental hoặc one-shot)
                    form_keywords = [
                        # Start form keywords
                        "bắt đầu điền", "mở form", "tạo form", "điền đơn", "làm đơn vay",
                        # Field keywords - MỞ RỘNG để catch nhiều hơn
                        "vay", "khoản vay", "đơn vay", "làm đơn vay", "tạo đơn vay",
                        "căn cước công dân", "căn cước", "số điện thoại", "sdt", "email", "địa chỉ",
                        "số tiền", "kỳ hạn", "mục đích vay", "thu nhập", "công ty",
                        "tên", "ngày sinh", "giới tính", "mục đích", "kỳ hạn",
                        # Common action keywords
                        "điền", "nhập", "điền vào", "cho", "là", "là",
                        # Submit keywords
                        "gửi form", "gửi đơn", "submit", "xong rồi", "làm xong"
                    ]
                    
                    # Push ngay khi detect intent (incremental mode - mỗi message push ngay)
                    # HOẶC nếu message có từ "điền" + tên/giá trị
                    has_form_intent = any(keyword in msg_lower for keyword in form_keywords)
                    has_fill_action = "điền" in msg_lower and len(msg_lower.split()) >= 2
                    
                    if has_form_intent or has_fill_action:
                        should_push_task = True
                        logger.info(f"🚀 Detected form intent in user message, pushing immediately to Browser Service")
                        logger.debug(f"   Message: {message.content[:100]}")
                        logger.debug(f"   Matched keywords: {[k for k in form_keywords if k in msg_lower]}")
                    else:
                        logger.debug(f"⚠️  No form intent detected in message: {message.content[:100]}")
                
                if should_push_task:
                    # Lấy TOÀN BỘ conversation history để extract thông tin
                    all_messages = transcript_data["messages"]
                    
                    # Format: "role: content" for each message
                    conversation_history = []
                    for m in all_messages:
                        conversation_history.append(f"{m['role']}: {m['content']}")
                    
                    # Join tất cả messages
                    full_context = "\n".join(conversation_history)
                    
                    logger.info(f"📤 Pushing request to Browser Service immediately...")
                    logger.info(f"   Full context ({len(all_messages)} messages) sent to Browser Service")
                    logger.info(f"   Latest user message: {message.content[:100]}...")
                    logger.info(f"   Session ID: {session_id}")
                    
                    # Set processing flag (cho phép nhiều push - incremental mode)
                    processing_task["active"] = True
                    processing_task["task_id"] = session_id
                    
                    # Push request to Browser Service (non-blocking - mỗi message push riêng)
                    try:
                        task = asyncio.create_task(push_to_browser_service(
                            full_context, ws_connections, session_id, processing_task
                        ))
                        logger.info(f"✅ Created async task for Browser Service request (task ID: {id(task)})")
                    except Exception as e:
                        logger.error(f"❌ Failed to create async task: {e}", exc_info=True)
                    
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

            Bạn hỗ trợ 5 loại form và LUÔN hành xử như một agent chủ động:
            - Tự động nhận diện khi người dùng nói ĐỦ thông tin → điền tất cả thông tin cùng lúc.
            - Nếu người dùng cung cấp theo TỪNG PHẦN → điền ngay từng field theo thời gian thực.
            - Tuyệt đối không hỏi hay nhắc đến “chế độ”.

            ---

            GỢI Ý NHANH:
            - Để điền nhanh, anh/chị chỉ cần NÓI MỘT LẦN đầy đủ thông tin khách hàng; tôi sẽ tự động trích xuất các trường cần thiết.
            - KHÔNG cần liệt kê từng mục theo thứ tự; chỉ cần nói tự nhiên, đủ ý.

            QUY TẮC PHONG CÁCH TRẢ LỜI (BẮT BUỘC):
            - Không dùng emoji hoặc icon trong bất kỳ câu trả lời nào.
            - Không dùng in đậm, không tiêu đề, không định dạng markdown đặc biệt.
            - Trả lời ngắn gọn, súc tích, câu thuần văn bản.
            - Nếu cần liệt kê, dùng dấu gạch đầu dòng "- " thuần văn bản.
            - Ví dụ sai: "🏦 Đơn vay vốn"; Ví dụ đúng: "- Đơn vay vốn & KYC".

            1️ **ĐƠN VAY VỐN & KYC** (Use Case 1)
            
            **ONE-SHOT:** "Vay 500 triệu Nguyễn Văn An Căn cước công dân 123... SĐT 0901..."
            → Xác nhận → Điền tất cả cùng lúc
            
            **INCREMENTAL:**
            - "Bắt đầu điền đơn vay" → Mở form
            - "Điền tên Hiếu Nghị" → Điền customerName
            - "Điền căn cước công dân 123456789123" → Điền customerId
            - "Điền số điện thoại 0963023600" → Điền phoneNumber
            - ... (từng field)
            - "Submit form" → Gửi đơn

            2️ **CẬP NHẬT CRM** (Use Case 2)
            - ONE-SHOT hoặc INCREMENTAL (tương tự)

            3️ **YÊU CẦU HR** (Use Case 3)
            - ONE-SHOT hoặc INCREMENTAL (tương tự)

            4️ **BÁO CÁO TUÂN THỦ** (Use Case 4)
            - ONE-SHOT hoặc INCREMENTAL (tương tự)

            5️ **KIỂM TRA GIAO DỊCH** (Use Case 5)
            - ONE-SHOT hoặc INCREMENTAL (tương tự)

            Khi người dùng cung cấp đủ thông tin trong một lần nói:

             **USER NÓI 1 CÂU DUY NHẤT** chứa TẤT CẢ thông tin
             **BOT GHI NHẬN** và nói "Đang xử lý..."
             **HỆ THỐNG TỰ ĐỘNG** push vào Browser Service → Xử lý ngay

            Khi người dùng cung cấp thông tin theo từng phần:

            BƯỚC 1: Bắt đầu form
            User: "Bắt đầu điền đơn vay" hoặc "Mở form vay"
            Bot: "Dạ, tôi đã mở form đơn vay. Anh/chị có thể bắt đầu điền từng thông tin."
            → System mở browser, navigate to form, GIỮ MỞ

            BƯỚC 2: Điền từng field (lặp lại nhiều lần)
            User: "Điền tên là Hiếu Nghị"
            Bot: "Đã điền tên. Tiếp tục điền hoặc nói 'Submit' khi xong."
            → System điền field customerName

            User: "Điền căn cước công dân 123456789123"
            Bot: "Đã điền Căn Cước Công Dân."
            → System điền field customerId

            User: "Điền số điện thoại 0963023600"
            Bot: "Đã điền số điện thoại."
            → System điền field phoneNumber

            User: "Vay 3 tỷ đồng"
            Bot: "Đã điền số tiền vay."
            → System điền field loanAmount

            (Cứ tiếp tục như vậy cho các fields khác...)

            BƯỚC 3: Submit
            User: "Submit form" hoặc "Gửi đơn" hoặc "Xong rồi"
            Bot: "Đang gửi form... Vui lòng đợi."
            → System click submit, xác nhận modal, đợi success
            → System đóng browser
            Bot: "Form đã được gửi thành công!"

            LƯU Ý CHO TRƯỜNG HỢP ĐIỀN TỪNG PHẦN:
            - KHÔNG cần xác nhận từng field (quá dài!)
            - User có thể nói NHIỀU FIELDS trong 1 câu: "Điền tên Hiếu Nghị và số điện thoại 0963023600"
            - Bot xác nhận ngắn gọn: "Đã điền tên và SĐT"
            - Sau khi user nói "Submit" → Hệ thống xử lý background → Bot thông báo khi xong
            KHÔNG BAO GIỜ ĐƯỢC Nói ra file Json 

            VÍ DỤ CHUẨN:

            **Use Case 1 - Loan:**
            User: "Tạo đơn vay cho khách hàng Nguyễn Văn An, căn cước công dân 012345678901, sinh 15/03/1985, địa chỉ 123 Lê Lợi Quận 1, SĐT 0901234567, email abc@gmail.com, vay 500 triệu mua nhà kỳ hạn 24 tháng, kỹ sư phần mềm FPT thu nhập 30 triệu/tháng"
            Bot: "Dạ, tôi đã ghi nhận: Nguyễn Văn An, căn cước công dân 012345678901, 500 triệu, 24 tháng. Đang xử lý..."
            (Hệ thống tự động push ngay - không cần confirm)

            **Use Case 2 - CRM:**
            User: "Cập nhật CRM khách Trần Văn B mã CUS002 khiếu nại thẻ bị khóa đã xử lý nhân viên Phạm Nam"
            Bot: "Dạ, tôi đã ghi nhận: KH Trần Văn B, mã CUS002, khiếu nại thẻ. Đang xử lý..."

            **Use Case 3 - HR:**
            User: "Đơn nghỉ phép nhân viên Trần Thị Cúc NV001 từ 22 đến 24/10 việc gia đình phòng Kinh Doanh quản lý Lê Hoàng"
            Bot: "Dạ, tôi đã ghi nhận: Trần Thị Cúc, nghỉ 22-24/10. Đang xử lý..."

            **Use Case 4 - Compliance:**
            User: "Báo cáo AML tháng 9 nhân viên Lê Văn Cường không vi phạm"
            Bot: "Dạ, tôi đã ghi nhận: Báo cáo AML tháng 9, Lê Văn Cường, 0 vi phạm. Đang xử lý..."

            **Use Case 5 - Operations:**
            User: "Kiểm tra GD TXN12345 số tiền 10 triệu khách Nguyễn Văn A"
            Bot: "Dạ, tôi đã ghi nhận: Mã TXN12345, 10 triệu đồng, KH Nguyễn Văn A. Đang xử lý..."

            ---

            QUY TRÌNH THỐNG NHẤT (2 BƯỚC):

            CHẾ ĐỘ TỰ ĐỘNG - KHÔNG CẦN XÁC NHẬN:
            
            - User nói thông tin (1 câu hoặc nhiều câu)
            - Bot ghi nhận và tự động xử lý ngay khi có đủ thông tin
            - Bot chỉ nói ngắn gọn: "Dạ, tôi đã ghi nhận: [tóm tắt]. Đang xử lý..."
            - Hệ thống tự động push vào Browser Service để điền form

            RÀNG BUỘC FORMAT & PHÁT ÂM (QUAN TRỌNG):

            **Số điện thoại:** 
            - Format: 10 chữ số, bắt đầu bằng 0
            - ĐỌC TỪNG SỐ KỸ LƯỠNG, RÕ RÀNG, NGẮT NHỊP NHẸ giữa từng số (0 9 6 3 0 2 3 6 0 0)
            - Tuyệt đối KHÔNG đọc ghép cặp/nhóm, KHÔNG nuốt số, KHÔNG đọc nhanh
            - Ví dụ ĐÚNG: "0963023600" → "không chín sáu ba không hai ba sáu không không"
            - Ví dụ SAI: "0963 023 600", "không chín sáu ba không hai ba sáu không", đọc dính/ghép nhóm
            - Khi bot NHẮC LẠI số điện thoại, vẫn đọc từng số tách bạch như trên (không hỏi xác nhận)

            **Số căn cước công dân:**
            - Format: 12 chữ số
            - Gọi: "Số Căn Cước Công Dân" (KHÔNG nói "CCCD" hay "căn cước công dân")
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

            ⚠️ QUAN TRỌNG - XỬ LÝ TỰ ĐỘNG:
            - KHÔNG cần xác nhận từ user
            - Khi đã thu thập đủ thông tin từ user, hệ thống sẽ TỰ ĐỘNG xử lý
            - Bot chỉ cần nói: "Dạ, tôi đã ghi nhận thông tin và đang xử lý..."
            - KHÔNG nói "BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ" nữa (đã bỏ confirm mode)
            
            ⚠️ CẤM:
            - KHÔNG hỏi xác nhận "Đúng không?"
            - KHÔNG chờ user xác nhận
            - Thu thập đủ thông tin → Tự động xử lý ngay
            - Không nói ra file Json

            VÍ DỤ CHUẨN:

            User: "Tôi muốn vay 500 triệu, tên Nguyễn Văn An, căn cước công dân001234567890"
            Bot: "Dạ, tôi đã ghi nhận: Nguyễn Văn An, căn cước công dân 001234567890, 500 triệu. Đang xử lý..."
            (Hệ thống tự động push ngay khi có đủ thông tin)

                        **VÍ DỤ AUTO MODE (Use Case 5):**

                        User: "Kiểm tra giao dịch TXN12345 số tiền 10 triệu khách hàng Nguyễn Văn A"
                        Bot: "Dạ, tôi đã ghi nhận: Mã TXN12345, 10 triệu đồng, KH Nguyễn Văn A. Đang xử lý..."
                        (Hệ thống tự động push ngay)
                        (Các fields khác như ngày GD, người kiểm tra sẽ auto-fill)

            TUYỆT ĐỐI KHÔNG:
            - Hỏi xác nhận "Đúng không?"
            - Chờ user xác nhận
            - Nói cụm "BẮT ĐẦU XỬ LÝ NGAY BÂY GIỜ" (đã bỏ mode này)
            - Trì hoãn xử lý khi đã có đủ thông tin

            ⏳ KHI ĐANG XỬ LÝ FORM (sau khi push vào Browser Service):
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
