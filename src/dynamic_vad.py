"""
Dynamic VAD Configuration
Automatically adjusts Voice Activity Detection parameters based on conversation context
"""
from typing import Dict, Optional
from enum import Enum
from pipecat.audio.vad.silero import VADParams
from loguru import logger


class ConversationContext(Enum):
    """Different conversation contexts requiring different VAD parameters"""
    GREETING = "greeting"  # Initial greeting, longer pauses OK
    FORM_FIELD = "form_field"  # Short answers (name, phone, etc.)
    LONG_ANSWER = "long_answer"  # Descriptions, explanations
    DIGIT_SEQUENCE = "digit_sequence"  # Phone numbers, CCCD
    CONFIRMATION = "confirmation"  # Yes/No answers
    DEFAULT = "default"  # Standard conversation


class DynamicVADConfig:
    """Manages context-aware VAD parameters"""

    # Predefined VAD configurations for different contexts
    VAD_CONFIGS: Dict[ConversationContext, Dict[str, float]] = {
        ConversationContext.GREETING: {
            "stop_secs": 4.0,  # Longer pauses OK for initial greeting
            "start_secs": 0.2,
            "min_volume": 0.6
        },
        ConversationContext.FORM_FIELD: {
            "stop_secs": 2.0,  # Quick responses (name, email, etc.)
            "start_secs": 0.1,
            "min_volume": 0.6
        },
        ConversationContext.LONG_ANSWER: {
            "stop_secs": 3.5,  # Allow pauses during long explanations
            "start_secs": 0.15,
            "min_volume": 0.6
        },
        ConversationContext.DIGIT_SEQUENCE: {
            "stop_secs": 3.0,  # User reads digits with pauses (0 9 6 3...)
            "start_secs": 0.1,
            "min_volume": 0.65  # Slightly higher to avoid noise
        },
        ConversationContext.CONFIRMATION: {
            "stop_secs": 1.5,  # Quick yes/no
            "start_secs": 0.1,
            "min_volume": 0.6
        },
        ConversationContext.DEFAULT: {
            "stop_secs": 3.0,  # Balanced for general conversation
            "start_secs": 0.1,
            "min_volume": 0.6
        }
    }

    def __init__(self):
        self.current_context = ConversationContext.DEFAULT
        self._message_count = 0

    def detect_context(self, message: str, role: str = "user") -> ConversationContext:
        """
        Detect conversation context from message content

        Args:
            message: User or bot message
            role: "user" or "assistant"

        Returns:
            ConversationContext enum
        """
        if role != "user":
            # For assistant messages, predict next user context
            return self._predict_next_context(message)

        message_lower = message.lower()

        # Greeting detection
        greeting_keywords = ["xin chào", "chào", "hello", "hi"]
        if self._message_count < 2 and any(kw in message_lower for kw in greeting_keywords):
            return ConversationContext.GREETING

        # Digit sequence detection (phone, CCCD)
        digit_keywords = ["số điện thoại", "sdt", "căn cước", "cccd", "mã số"]
        if any(kw in message_lower for kw in digit_keywords):
            return ConversationContext.DIGIT_SEQUENCE

        # Confirmation detection
        confirmation_keywords = ["đúng", "không", "có", "được", "xác nhận", "submit", "gửi"]
        if len(message.split()) <= 3 and any(kw in message_lower for kw in confirmation_keywords):
            return ConversationContext.CONFIRMATION

        # Form field detection (short answers)
        form_field_keywords = ["tên", "địa chỉ", "email", "điền", "là", "cho"]
        if any(kw in message_lower for kw in form_field_keywords) and len(message.split()) <= 8:
            return ConversationContext.FORM_FIELD

        # Long answer detection
        if len(message.split()) > 15:
            return ConversationContext.LONG_ANSWER

        return ConversationContext.DEFAULT

    def _predict_next_context(self, bot_message: str) -> ConversationContext:
        """Predict next user context based on bot's question"""
        bot_lower = bot_message.lower()

        # Bot asking for phone/CCCD
        if any(kw in bot_lower for kw in ["số điện thoại", "căn cước", "cccd"]):
            return ConversationContext.DIGIT_SEQUENCE

        # Bot asking for confirmation
        if any(kw in bot_lower for kw in ["đúng không", "xác nhận", "có đúng"]):
            return ConversationContext.CONFIRMATION

        # Bot asking for name, email, etc
        if any(kw in bot_lower for kw in ["tên", "email", "địa chỉ"]):
            return ConversationContext.FORM_FIELD

        return ConversationContext.DEFAULT

    def get_vad_params(self, context: Optional[ConversationContext] = None) -> VADParams:
        """
        Get VAD parameters for given context

        Args:
            context: Optional context override, uses current_context if None

        Returns:
            VADParams configured for the context
        """
        ctx = context or self.current_context
        config = self.VAD_CONFIGS[ctx]

        logger.debug(f"🎙️ VAD Config for {ctx.value}: stop={config['stop_secs']}s, start={config['start_secs']}s")

        return VADParams(
            stop_secs=config["stop_secs"],
            start_secs=config["start_secs"],
            min_volume=config["min_volume"]
        )

    def update_context(self, message: str, role: str = "user"):
        """
        Update current context based on new message

        Args:
            message: New message content
            role: Message role
        """
        new_context = self.detect_context(message, role)

        if new_context != self.current_context:
            logger.info(f"📍 VAD Context changed: {self.current_context.value} → {new_context.value}")
            self.current_context = new_context

        if role == "user":
            self._message_count += 1

    def reset(self):
        """Reset context to default (for new conversation)"""
        self.current_context = ConversationContext.DEFAULT
        self._message_count = 0
        logger.info("🔄 VAD context reset to default")


# Global instance
vad_config = DynamicVADConfig()
