"""
Advanced Features - Tận dụng full tech stack
- Multi-model LLM routing (Bedrock + OpenAI)
- Smart caching with DynamoDB
- Voice cloning with ElevenLabs
- Real-time collaboration
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from loguru import logger

# AWS imports
import boto3
from botocore.exceptions import ClientError

# OpenAI import
from openai import AsyncOpenAI


class MultiModelRouter:
    """
    Smart LLM routing between Bedrock and OpenAI
    - Use Bedrock (Claude) for complex reasoning
    - Use OpenAI for fast responses
    - Automatic fallback on errors
    """
    
    def __init__(self):
        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        self.openai_client = AsyncOpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        self.bedrock_model = os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-sonnet-4-20250514-v1:0')
        self.openai_model = "gpt-4o-mini"  # Fast and cheap
        
        self.stats = {
            "bedrock_calls": 0,
            "openai_calls": 0,
            "bedrock_errors": 0,
            "openai_errors": 0,
        }
    
    async def route_request(
        self,
        prompt: str,
        task_type: str = "general",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Route request to appropriate model based on task type
        
        Args:
            prompt: User prompt
            task_type: Type of task (complex/fast/creative)
            max_tokens: Max response tokens
            temperature: Temperature for generation
            
        Returns:
            Response dict with text and metadata
        """
        # Route based on task type
        if task_type == "complex":
            # Use Bedrock for complex reasoning
            return await self._call_bedrock(prompt, max_tokens, temperature)
        elif task_type == "fast":
            # Use OpenAI for fast responses
            return await self._call_openai(prompt, max_tokens, temperature)
        else:
            # Try Bedrock first, fallback to OpenAI
            try:
                return await self._call_bedrock(prompt, max_tokens, temperature)
            except Exception as e:
                logger.warning(f"Bedrock failed, falling back to OpenAI: {e}")
                return await self._call_openai(prompt, max_tokens, temperature)
    
    async def _call_bedrock(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Call AWS Bedrock (Claude)"""
        try:
            self.stats["bedrock_calls"] += 1
            
            # Prepare request
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Call Bedrock
            response = self.bedrock_client.invoke_model(
                modelId=self.bedrock_model,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            text = response_body['content'][0]['text']
            
            return {
                "success": True,
                "text": text,
                "model": "bedrock-claude",
                "tokens": response_body.get('usage', {})
            }
            
        except Exception as e:
            self.stats["bedrock_errors"] += 1
            logger.error(f"Bedrock error: {e}")
            raise
    
    async def _call_openai(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Call OpenAI API"""
        try:
            self.stats["openai_calls"] += 1
            
            # Call OpenAI
            response = await self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            text = response.choices[0].message.content
            
            return {
                "success": True,
                "text": text,
                "model": "openai-gpt4o-mini",
                "tokens": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            self.stats["openai_errors"] += 1
            logger.error(f"OpenAI error: {e}")
            raise
    
    def get_stats(self) -> Dict[str, int]:
        """Get usage statistics"""
        return self.stats.copy()


class SmartCache:
    """
    Smart caching with DynamoDB
    - Cache LLM responses
    - Cache form data
    - Cache user preferences
    """
    
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('DYNAMODB_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('DYNAMODB_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('DYNAMODB_SECRET_ACCESS_KEY')
        )
        
        self.table_name = os.getenv('DYNAMODB_TABLE_NAME', 'vpbank-sessions')
        self.table = self.dynamodb.Table(self.table_name)
        
        self.cache_ttl = 3600  # 1 hour
    
    async def get_cached_response(
        self,
        cache_key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached response
        
        Args:
            cache_key: Cache key (hash of prompt)
            
        Returns:
            Cached response or None
        """
        try:
            response = self.table.get_item(
                Key={'session_id': f"cache_{cache_key}"}
            )
            
            if 'Item' not in response:
                return None
            
            item = response['Item']
            
            # Check if expired
            cached_at = datetime.fromisoformat(item.get('cached_at', '2000-01-01'))
            if datetime.now() - cached_at > timedelta(seconds=self.cache_ttl):
                logger.info(f"Cache expired for {cache_key}")
                return None
            
            logger.info(f"Cache hit for {cache_key}")
            return item.get('response')
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set_cached_response(
        self,
        cache_key: str,
        response: Dict[str, Any]
    ):
        """
        Set cached response
        
        Args:
            cache_key: Cache key
            response: Response to cache
        """
        try:
            self.table.put_item(
                Item={
                    'session_id': f"cache_{cache_key}",
                    'response': response,
                    'cached_at': datetime.now().isoformat(),
                    'ttl': int((datetime.now() + timedelta(seconds=self.cache_ttl)).timestamp())
                }
            )
            logger.info(f"Cached response for {cache_key}")
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    async def get_user_preferences(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Get user preferences from cache"""
        try:
            response = self.table.get_item(
                Key={'session_id': f"pref_{user_id}"}
            )
            
            if 'Item' in response:
                return response['Item'].get('preferences', {})
            
            return {}
            
        except Exception as e:
            logger.error(f"Get preferences error: {e}")
            return {}
    
    async def set_user_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ):
        """Set user preferences"""
        try:
            self.table.put_item(
                Item={
                    'session_id': f"pref_{user_id}",
                    'preferences': preferences,
                    'updated_at': datetime.now().isoformat()
                }
            )
            logger.info(f"Saved preferences for {user_id}")
            
        except Exception as e:
            logger.error(f"Set preferences error: {e}")


class VoiceEnhancer:
    """
    Enhanced voice features with ElevenLabs
    - Voice cloning
    - Emotion control
    - Multi-voice support
    """
    
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        self.voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'XBDAUT8ybuJTTCoOLSUj')
        
        # Voice presets for different scenarios
        self.voice_presets = {
            "professional": {
                "stability": 0.75,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            },
            "friendly": {
                "stability": 0.50,
                "similarity_boost": 0.75,
                "style": 0.5,
                "use_speaker_boost": True
            },
            "empathetic": {
                "stability": 0.60,
                "similarity_boost": 0.80,
                "style": 0.7,
                "use_speaker_boost": True
            }
        }
    
    async def generate_speech(
        self,
        text: str,
        voice_style: str = "professional",
        output_format: str = "mp3_44100_128"
    ) -> bytes:
        """
        Generate speech with emotion control
        
        Args:
            text: Text to speak
            voice_style: Voice style (professional/friendly/empathetic)
            output_format: Audio format
            
        Returns:
            Audio bytes
        """
        import httpx
        
        preset = self.voice_presets.get(voice_style, self.voice_presets["professional"])
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": preset
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"ElevenLabs error: {response.status_code}")
                raise Exception(f"TTS failed: {response.text}")
    
    async def detect_emotion(self, text: str) -> str:
        """
        Detect emotion from text to choose appropriate voice style
        
        Args:
            text: Input text
            
        Returns:
            Emotion (professional/friendly/empathetic)
        """
        text_lower = text.lower()
        
        # Empathetic keywords
        if any(word in text_lower for word in ["xin lỗi", "tiếc", "buồn", "khó khăn", "vấn đề"]):
            return "empathetic"
        
        # Friendly keywords
        if any(word in text_lower for word in ["cảm ơn", "tuyệt", "tốt", "vui", "haha"]):
            return "friendly"
        
        # Default professional
        return "professional"


class CollaborationManager:
    """
    Real-time collaboration features
    - Share form sessions
    - Co-editing
    - Activity tracking
    """
    
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('DYNAMODB_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('DYNAMODB_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('DYNAMODB_SECRET_ACCESS_KEY')
        )
        
        self.table_name = os.getenv('DYNAMODB_TABLE_NAME', 'vpbank-sessions')
        self.table = self.dynamodb.Table(self.table_name)
    
    async def share_session(
        self,
        session_id: str,
        owner_id: str,
        shared_with: List[str],
        permissions: str = "view"
    ) -> Dict[str, Any]:
        """
        Share session with other users
        
        Args:
            session_id: Session to share
            owner_id: Owner user ID
            shared_with: List of user IDs to share with
            permissions: Permissions (view/edit)
            
        Returns:
            Share result
        """
        try:
            share_id = f"share_{session_id}"
            
            self.table.put_item(
                Item={
                    'session_id': share_id,
                    'original_session': session_id,
                    'owner_id': owner_id,
                    'shared_with': shared_with,
                    'permissions': permissions,
                    'shared_at': datetime.now().isoformat()
                }
            )
            
            logger.info(f"Shared session {session_id} with {len(shared_with)} users")
            
            return {
                "success": True,
                "share_id": share_id,
                "shared_with": shared_with
            }
            
        except Exception as e:
            logger.error(f"Share session error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_shared_sessions(
        self,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Get all sessions shared with user"""
        try:
            # Scan for sessions shared with this user
            response = self.table.scan(
                FilterExpression='contains(shared_with, :user_id)',
                ExpressionAttributeValues={':user_id': user_id}
            )
            
            return response.get('Items', [])
            
        except Exception as e:
            logger.error(f"Get shared sessions error: {e}")
            return []
    
    async def log_activity(
        self,
        session_id: str,
        user_id: str,
        action: str,
        details: Dict[str, Any]
    ):
        """Log user activity for collaboration tracking"""
        try:
            activity_id = f"activity_{session_id}_{datetime.now().timestamp()}"
            
            self.table.put_item(
                Item={
                    'session_id': activity_id,
                    'original_session': session_id,
                    'user_id': user_id,
                    'action': action,
                    'details': details,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Log activity error: {e}")


# Global instances
multi_model_router = MultiModelRouter()
smart_cache = SmartCache()
voice_enhancer = VoiceEnhancer()
collaboration_manager = CollaborationManager()


# Convenience functions
async def route_llm_request(prompt: str, task_type: str = "general") -> Dict[str, Any]:
    """Route LLM request to best model"""
    return await multi_model_router.route_request(prompt, task_type)


async def get_cached_or_generate(cache_key: str, generator_func) -> Dict[str, Any]:
    """Get from cache or generate new"""
    cached = await smart_cache.get_cached_response(cache_key)
    if cached:
        return cached
    
    result = await generator_func()
    await smart_cache.set_cached_response(cache_key, result)
    return result


async def speak_with_emotion(text: str) -> bytes:
    """Generate speech with automatic emotion detection"""
    emotion = await voice_enhancer.detect_emotion(text)
    return await voice_enhancer.generate_speech(text, emotion)
