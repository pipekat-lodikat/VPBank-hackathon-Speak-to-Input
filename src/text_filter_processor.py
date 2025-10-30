"""
Text Filter Processor - Remove internal markers before TTS
Filters out [CONFIRM_AND_EXECUTE] and other markers from LLM output
"""
from pipecat.processors.frame_processor import FrameProcessor
from pipecat.frames.frames import TextFrame, Frame
from loguru import logger


class TextFilterProcessor(FrameProcessor):
    """
    Filter processor để loại bỏ internal markers trước khi TTS đọc
    """
    
    def __init__(self):
        super().__init__()
        self.markers_to_filter = [
            "[CONFIRM_AND_EXECUTE]",
            "[EXECUTE]",
            "[CONFIRMED]"
        ]
    
    async def process_frame(self, frame: Frame, direction):
        """Process frames and filter text markers"""
        
        # Only filter TextFrames (LLM output text)
        if isinstance(frame, TextFrame):
            original_text = frame.text
            filtered_text = original_text
            
            # Remove all markers
            for marker in self.markers_to_filter:
                if marker in filtered_text:
                    logger.debug(f"🔇 Filtering marker: {marker}")
                    filtered_text = filtered_text.replace(marker, "")
            
            # Clean up extra whitespace
            filtered_text = filtered_text.strip()
            
            # Create new frame with filtered text
            if filtered_text != original_text:
                frame = TextFrame(text=filtered_text)
                logger.debug(f"📝 Filtered: '{original_text}' → '{filtered_text}'")
        
        # Pass frame to next processor
        await self.push_frame(frame, direction)


# Export
__all__ = ["TextFilterProcessor"]

