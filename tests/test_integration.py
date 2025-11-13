"""
Integration Tests for VPBank Voice Agent
Tests service-to-service communication
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import aiohttp
from aiohttp import web


class TestIntegration:
    """Integration tests for service communication"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_voice_bot_to_browser_agent_communication(
        self,
        mock_env_vars,
        mock_aiohttp_session
    ):
        """Test Voice Bot sending request to Browser Agent"""
        # Simulate voice bot sending request to browser agent
        user_message = "Điền đơn vay cho khách hàng Nguyen Van An"
        session_id = "test-session-123"
        
        browser_service_url = "http://localhost:7863"
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session_class.return_value = mock_aiohttp_session
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "user_message": user_message,
                    "session_id": session_id
                }
                
                async with session.post(
                    f"{browser_service_url}/api/execute",
                    json=payload
                ) as response:
                    assert response.status == 200
                    data = await response.json()
                    assert data["success"] is True
                    assert "result" in data

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_frontend_to_voice_bot_webrtc_flow(self, mock_env_vars):
        """Test frontend initiating WebRTC connection with Voice Bot"""
        # Simulate WebRTC offer from frontend
        offer_sdp = "v=0\r\no=- 123456789 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\n"
        
        # Create test server
        app = web.Application()
        
        async def mock_offer_handler(request):
            data = await request.json()
            assert data["type"] == "offer"
            assert "sdp" in data
            
            # Return mock answer
            return web.json_response({
                "type": "answer",
                "sdp": "v=0\r\no=- 987654321 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\n"
            })
        
        app.router.add_post('/offer', mock_offer_handler)
        
        # Start test server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 8765)
        await site.start()
        
        try:
            # Test WebRTC offer
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'http://localhost:8765/offer',
                    json={"type": "offer", "sdp": offer_sdp}
                ) as response:
                    assert response.status == 200
                    data = await response.json()
                    assert data["type"] == "answer"
                    assert "sdp" in data
        finally:
            await runner.cleanup()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_end_to_end_form_filling_flow(
        self,
        mock_env_vars,
        sample_form_data,
        mock_aiohttp_session
    ):
        """Test complete end-to-end form filling flow"""
        # Step 1: User initiates voice session
        session_id = "e2e-test-session"
        
        # Step 2: Voice Bot receives transcript
        user_message = (
            "Tạo đơn vay cho khách hàng Nguyen Van An, "
            "căn cước công dân 012345678901, SĐT 0901234567"
        )
        
        # Step 3: Voice Bot extracts data and sends to Browser Agent
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session_class.return_value = mock_aiohttp_session

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'http://localhost:7863/api/execute',
                    json={
                        "user_message": user_message,
                        "session_id": session_id
                    }
                ) as response:
                    assert response.status == 200
                    data = await response.json()
                    assert data["success"] is True

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_websocket_transcript_streaming(self, mock_env_vars):
        """Test WebSocket transcript streaming from Voice Bot to Frontend"""
        app = web.Application()
        messages_received = []
        
        async def websocket_handler(request):
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            
            # Simulate sending transcript messages
            await ws.send_json({
                "type": "transcript",
                "role": "user",
                "content": "Test message",
                "timestamp": "2025-01-01T00:00:00Z"
            })
            
            # Wait for client response
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    messages_received.append(msg.data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
            
            return ws
        
        app.router.add_get('/ws', websocket_handler)
        
        # Start test server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 8766)
        await site.start()
        
        try:
            # Connect to WebSocket
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect('http://localhost:8766/ws') as ws:
                    # Receive transcript message
                    msg = await ws.receive_json()
                    assert msg["type"] == "transcript"
                    assert msg["role"] == "user"
                    assert msg["content"] == "Test message"
        finally:
            await runner.cleanup()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_authentication_flow(self, mock_env_vars, mock_cognito_client):
        """Test authentication flow with Cognito"""
        with patch('src.auth_service.boto3.client') as mock_boto_client:
            mock_boto_client.return_value = mock_cognito_client
            
            from src.auth_service import CognitoAuthService
            
            auth_service = CognitoAuthService()
            
            # Test login
            result = await auth_service.login("testuser", "testpass123")
            assert result["success"] is True
            assert "access_token" in result
            
            # Test token verification
            user_info = await auth_service.verify_token(result["access_token"])
            assert user_info is not None
            assert user_info["username"] == "testuser"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_session_storage_flow(
        self,
        mock_env_vars,
        mock_dynamodb_client,
        sample_session_data
    ):
        """Test session storage with DynamoDB"""
        with patch('src.dynamodb_service.boto3.resource') as mock_boto_resource:
            mock_boto_resource.return_value = mock_dynamodb_client
            
            from src.dynamodb_service import DynamoDBService
            
            dynamodb = DynamoDBService()
            
            # Save session
            result = dynamodb.save_session(sample_session_data)
            assert result is True
            
            # Retrieve session
            session = dynamodb.get_session(sample_session_data["session_id"])
            assert session is not None
            assert session["session_id"] == sample_session_data["session_id"]
            
            # List sessions
            sessions = dynamodb.list_sessions(limit=10)
            assert sessions["count"] >= 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_error_handling_across_services(self, mock_env_vars):
        """Test error handling when Browser Agent is unavailable"""
        # Simulate Browser Agent being down
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.side_effect = (
                aiohttp.ClientConnectionError()
            )
            
            # Voice Bot should handle the error gracefully
            with pytest.raises(aiohttp.ClientConnectionError):
                async with aiohttp.ClientSession() as session:
                    await session.post(
                        'http://localhost:7863/api/execute',
                        json={"user_message": "test", "session_id": "test"}
                    )

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_concurrent_sessions(self, mock_env_vars, mock_aiohttp_session):
        """Test handling multiple concurrent voice sessions"""
        num_sessions = 5
        
        async def create_session(session_id):
            with patch('aiohttp.ClientSession') as mock_session_class:
                mock_session_class.return_value = mock_aiohttp_session
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        'http://localhost:7863/api/execute',
                        json={
                            "user_message": f"Test message {session_id}",
                            "session_id": session_id
                        }
                    ) as response:
                        return await response.json()
        
        # Create multiple sessions concurrently
        tasks = [create_session(f"session-{i}") for i in range(num_sessions)]
        results = await asyncio.gather(*tasks)
        
        # Verify all sessions succeeded
        assert len(results) == num_sessions
        for result in results:
            assert result["success"] is True

