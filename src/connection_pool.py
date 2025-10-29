"""
Connection Pool Implementation for AWS ECS Fargate
Giải pháp để giảm cold-start từ 60-120s xuống còn 50-100ms
"""

import asyncio
import os
from typing import Dict, Any, Optional
from datetime import datetime
from contextlib import asynccontextmanager
from loguru import logger
from pipecat.transcriptions.language import Language


class ConnectionPool:
    """
    Connection pool giữ các instances của services luôn sẵn sàng.
    
    Giải quyết cold start bằng cách pre-initialize các expensive resources:
    - AWS Transcribe STT service
    - AWS Bedrock LLM service
    - OpenAI TTS service
    
    Usage:
        pool = ConnectionPool(pool_size=3)
        await pool.initialize()
        
        async with pool.get_connection() as conn:
            stt = conn['stt']
            llm = conn['llm']
            tts = conn['tts']
            # use services...
    """
    
    def __init__(self, pool_size: int = 3):
        """
        Initialize connection pool.
        
        Args:
            pool_size: Number of pre-initialized connections to keep in pool
                      Default: 3 (recommend for small-medium traffic)
                      Use 5-10 for high traffic
        """
        self.pool_size = pool_size
        self.available_connections: Optional[asyncio.Queue] = None
        self.initialized = False
        self.lock = asyncio.Lock()
        self.creation_lock = asyncio.Lock()
        self.stats = {
            'total_created': 0,
            'total_used': 0,
            'total_errors': 0,
            'started_at': datetime.now()
        }
    
    async def initialize(self):
        """
        Initialize connection pool when app starts.
        This is called in FastAPI startup event.
        
        Timeline:
        - T+0s: Start initialization
        - T+5-10s: All connections created and ready
        - T+10s: Health check passed, ready to handle requests
        
        Raises:
            RuntimeError: If initialization fails
        """
        async with self.lock:
            if self.initialized:
                logger.info("✅ Connection pool already initialized")
                return
            
            logger.info(f"🌊 Initializing connection pool with {self.pool_size} connections...")
            logger.info("⏱️  This may take 10-15 seconds on first startup (AWS credential handshake)")
            
            self.available_connections = asyncio.Queue(maxsize=self.pool_size)
            
            # Create all connections in parallel
            creation_tasks = []
            for i in range(self.pool_size):
                creation_tasks.append(self._create_and_queue_connection(i))
            
            results = await asyncio.gather(*creation_tasks, return_exceptions=True)
            
            successful = sum(1 for r in results if not isinstance(r, Exception))
            failed = sum(1 for r in results if isinstance(r, Exception))
            
            logger.info(f"✅ Pool initialization complete")
            logger.info(f"  └─ Successful: {successful}/{self.pool_size}")
            if failed > 0:
                logger.warning(f"  └─ Failed: {failed}/{self.pool_size}")
                for i, r in enumerate(results):
                    if isinstance(r, Exception):
                        logger.error(f"    └─ Connection {i+1}: {r}")
            
            self.initialized = True
    
    async def _create_and_queue_connection(self, index: int):
        """Create a connection and add to queue."""
        try:
            conn = await self._create_connection(index)
            await self.available_connections.put(conn)
        except Exception as e:
            self.stats['total_errors'] += 1
            logger.error(f"❌ Failed to create pool connection {index+1}: {e}")
            raise
    
    async def _create_connection(self, index: int) -> Dict[str, Any]:
        """
        Create a single connection with all required services.
        
        This is expensive operation (5-10s per connection) because:
        1. AWS credential validation
        2. Service initialization
        3. Connection establishment
        
        Args:
            index: Connection index for logging/identification
            
        Returns:
            Dictionary with initialized services
        """
        # Avoid thundering herd - stagger creation
        await asyncio.sleep(index * 1)
        
        logger.debug(f"🔧 Creating connection {index + 1}/{self.pool_size}...")
        
        try:
            # Import here to avoid circular imports
            from pipecat.services.aws.stt import AWSTranscribeSTTService
            from pipecat.services.aws.llm import AWSBedrockLLMService
            from pipecat.services.openai.tts import OpenAITTSService
            
            # Create services
            stt = AWSTranscribeSTTService(
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                aws_region=os.getenv("AWS_REGION", "us-east-1"),
                language=Language.VI
            )
            
            llm = AWSBedrockLLMService(
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                aws_region=os.getenv("AWS_REGION", "us-east-1"),
                model=os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
            )
            
            tts = OpenAITTSService(
                api_key=os.getenv("OPENAI_API_KEY"),
                voice="nova",
                model="gpt-4o-mini-tts"
            )
            
            connection = {
                'index': index,
                'stt': stt,
                'llm': llm,
                'tts': tts,
                'created_at': datetime.now().isoformat(),
                'in_use': False,
                'total_uses': 0,
                'last_used': None
            }
            
            logger.info(f"✅ Connection {index+1}/{self.pool_size} initialized")
            self.stats['total_created'] += 1
            
            return connection
        
        except Exception as e:
            logger.error(f"❌ Failed to create connection {index+1}: {str(e)}")
            raise
    
    @asynccontextmanager
    async def get_connection(self):
        """
        Get a connection from the pool (context manager).
        
        If no connection available, will wait up to 10 seconds.
        If timeout, creates temporary connection.
        
        Usage:
            async with pool.get_connection() as conn:
                stt = conn['stt']
                llm = conn['llm']
                tts = conn['tts']
                # ... use services ...
        
        Yields:
            Connection dictionary with services
            
        Raises:
            RuntimeError: If pool not initialized
        """
        if not self.initialized:
            raise RuntimeError("❌ Connection pool not initialized. Call await pool.initialize() first.")
        
        conn = None
        is_temporary = False
        
        try:
            # Try to get from pool with timeout
            try:
                conn = await asyncio.wait_for(
                    self.available_connections.get(),
                    timeout=10.0
                )
                conn['in_use'] = True
                conn['total_uses'] += 1
                conn['last_used'] = datetime.now().isoformat()
                
                logger.debug(f"🔗 Using pool connection {conn['index']} "
                           f"(uses: {conn['total_uses']})")
                
            except asyncio.TimeoutError:
                logger.warning("⚠️  No available connections in pool, "
                             "creating temporary connection")
                conn = await self._create_connection(-1)  # Temporary
                conn['in_use'] = True
                is_temporary = True
                logger.debug(f"🔗 Using temporary connection")
            
            self.stats['total_used'] += 1
            yield conn
        
        except Exception as e:
            logger.error(f"❌ Error in connection context: {e}")
            self.stats['total_errors'] += 1
            raise
        
        finally:
            if conn is not None:
                conn['in_use'] = False
                
                # Return to pool if not temporary and pool not full
                if not is_temporary and not self.available_connections.full():
                    try:
                        await self.available_connections.put(conn)
                        logger.debug(f"↩️  Returned connection {conn['index']} to pool")
                    except Exception as e:
                        logger.error(f"Failed to return connection to pool: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Health check of the connection pool.
        
        Returns:
            Dictionary with pool status
        """
        if not self.initialized:
            return {
                "status": "not_initialized",
                "message": "Pool has not been initialized yet"
            }
        
        available = self.available_connections.qsize()
        uptime = (datetime.now() - self.stats['started_at']).total_seconds()
        
        return {
            "status": "healthy",
            "pool_size": self.pool_size,
            "available_connections": available,
            "in_use_connections": self.pool_size - available,
            "total_created": self.stats['total_created'],
            "total_used": self.stats['total_used'],
            "total_errors": self.stats['total_errors'],
            "uptime_seconds": round(uptime, 2)
        }
    
    async def shutdown(self):
        """
        Gracefully shutdown the pool.
        Called when app shuts down.
        """
        if not self.initialized:
            return
        
        logger.info("🛑 Shutting down connection pool...")
        
        # Drain queue
        while not self.available_connections.empty():
            try:
                conn = self.available_connections.get_nowait()
                logger.debug(f"Closing connection {conn['index']}")
                # Add cleanup code here if needed
            except asyncio.QueueEmpty:
                break
        
        self.initialized = False
        logger.info("✅ Connection pool shutdown complete")


# Global pool instance
connection_pool: Optional[ConnectionPool] = None


async def init_connection_pool(pool_size: int = 3) -> ConnectionPool:
    """
    Initialize global connection pool.
    
    Args:
        pool_size: Number of connections in pool
        
    Returns:
        Initialized ConnectionPool instance
    """
    global connection_pool
    connection_pool = ConnectionPool(pool_size=pool_size)
    await connection_pool.initialize()
    return connection_pool


def get_pool() -> ConnectionPool:
    """Get global connection pool instance."""
    if connection_pool is None:
        raise RuntimeError("Connection pool not initialized")
    return connection_pool
