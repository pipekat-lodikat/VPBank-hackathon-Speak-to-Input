"""
Unit Tests for Browser Agent Service
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from src.browser_agent import BrowserAgentHandler
from src.exceptions import (
    BrowserSessionNotFoundError,
    BrowserNavigationError,
    BrowserFieldNotFoundError,
)


class TestBrowserAgentHandler:
    """Test suite for BrowserAgentHandler"""

    @pytest.fixture
    def browser_agent(self, mock_env_vars):
        """Create BrowserAgentHandler instance for testing"""
        return BrowserAgentHandler()

    def test_initialization(self, browser_agent):
        """Test BrowserAgentHandler initialization"""
        assert browser_agent.sessions == {}
        assert browser_agent.llm is None
        assert browser_agent.browser is None

    def test_get_llm(self, browser_agent, mock_env_vars):
        """Test LLM initialization"""
        with patch('src.browser_agent.ChatOpenAI') as mock_chat:
            mock_chat.return_value = Mock()
            llm = browser_agent._get_llm()
            
            assert llm is not None
            assert browser_agent.llm is not None
            mock_chat.assert_called_once_with(model="gpt-4o", temperature=0)

    @pytest.mark.asyncio
    async def test_ensure_browser(self, browser_agent, mock_browser):
        """Test browser initialization"""
        with patch('src.browser_agent.Browser') as mock_browser_class:
            mock_browser_class.return_value = mock_browser
            browser = await browser_agent._ensure_browser()
            
            assert browser is not None
            assert browser_agent.browser is not None

    @pytest.mark.asyncio
    async def test_start_form_session_success(self, browser_agent, mock_browser):
        """Test starting a form session successfully"""
        form_url = "https://vpbank-shared-form-fastdeploy.vercel.app/"
        form_type = "loan"
        session_id = "test-session-123"
        
        with patch.object(browser_agent, '_ensure_browser', return_value=mock_browser):
            with patch.object(browser_agent, '_get_llm', return_value=Mock()):
                with patch('src.browser_agent.BrowserUseAgent') as mock_agent:
                    # Mock agent
                    mock_agent_instance = AsyncMock()
                    mock_agent_instance.run = AsyncMock()
                    mock_agent.return_value = mock_agent_instance
                    
                    result = await browser_agent.start_form_session(
                        form_url=form_url,
                        form_type=form_type,
                        session_id=session_id
                    )
                    
                    assert result["success"] is True
                    assert "message" in result
                    assert session_id in browser_agent.sessions
                    assert browser_agent.sessions[session_id]["session_data"]["type"] == form_type

    @pytest.mark.asyncio
    async def test_start_form_session_reuse(self, browser_agent):
        """Test reusing existing session"""
        session_id = "test-session-123"
        
        # Setup existing session
        mock_agent = AsyncMock()
        mock_agent.add_new_task = Mock()
        mock_agent.run = AsyncMock()
        
        browser_agent.sessions[session_id] = {
            "agent": mock_agent,
            "session_data": {
                "url": "https://test.com",
                "type": "loan",
                "fields_filled": [],
                "session_id": session_id
            }
        }
        
        result = await browser_agent.start_form_session(
            form_url="https://test.com",
            form_type="loan",
            session_id=session_id
        )
        
        assert result["success"] is True
        assert "Reusing" in result["message"]
        mock_agent.add_new_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_fill_field_incremental_success(self, browser_agent):
        """Test filling a single field incrementally"""
        session_id = "test-session-123"
        field_name = "customerName"
        value = "Nguyen Van An"
        
        # Setup session
        mock_agent = AsyncMock()
        mock_agent.add_new_task = Mock()
        mock_agent.run = AsyncMock()
        
        browser_agent.sessions[session_id] = {
            "agent": mock_agent,
            "session_data": {
                "fields_filled": []
            }
        }
        
        result = await browser_agent.fill_field_incremental(
            field_name=field_name,
            value=value,
            session_id=session_id
        )
        
        assert result["success"] is True
        assert result["field"] == field_name
        assert result["value"] == value
        assert len(browser_agent.sessions[session_id]["session_data"]["fields_filled"]) == 1

    @pytest.mark.asyncio
    async def test_fill_field_no_session(self, browser_agent):
        """Test filling field without active session"""
        result = await browser_agent.fill_field_incremental(
            field_name="test",
            value="test",
            session_id="nonexistent"
        )
        
        assert result["success"] is False
        assert "No active session" in result["error"]

    @pytest.mark.asyncio
    async def test_fill_field_skip_duplicate(self, browser_agent):
        """Test skipping duplicate field fill"""
        session_id = "test-session-123"
        field_name = "customerName"
        value = "Nguyen Van An"
        
        # Setup session with already filled field
        browser_agent.sessions[session_id] = {
            "agent": AsyncMock(),
            "session_data": {
                "fields_filled": [
                    {"field": field_name, "value": value}
                ]
            }
        }
        
        result = await browser_agent.fill_field_incremental(
            field_name=field_name,
            value=value,
            session_id=session_id
        )
        
        assert result["success"] is True
        assert result.get("skipped") is True

    @pytest.mark.asyncio
    async def test_fill_fields_parallel_success(self, browser_agent):
        """Test filling multiple fields in parallel"""
        session_id = "test-session-123"
        fields = {
            "customerName": "Nguyen Van An",
            "phoneNumber": "0901234567",
            "email": "test@example.com"
        }
        
        # Setup session
        mock_agent = AsyncMock()
        mock_agent.add_new_task = Mock()
        mock_agent.run = AsyncMock()
        
        browser_agent.sessions[session_id] = {
            "agent": mock_agent,
            "session_data": {
                "fields_filled": []
            }
        }
        
        result = await browser_agent.fill_fields_parallel(
            fields=fields,
            session_id=session_id
        )
        
        assert result["success"] is True
        assert result["fields_count"] == 3
        assert len(browser_agent.sessions[session_id]["session_data"]["fields_filled"]) == 3

    @pytest.mark.asyncio
    async def test_summarize_filled_fields(self, browser_agent):
        session_id = "summary-session"
        browser_agent.sessions[session_id] = {
            "agent": AsyncMock(),
            "session_data": {
                "fields_filled": [
                    {"field": "customerName", "value": "Nguyen Van An"},
                    {"field": "phoneNumber", "value": "0901234567"}
                ]
            }
        }

        result = await browser_agent.summarize_filled_fields(session_id=session_id)

        assert result["success"] is True
        assert "Nguyen Van An" in result["message"]
        assert len(result["fields"]) == 2

    @pytest.mark.asyncio
    async def test_read_field_value_found(self, browser_agent):
        session_id = "read-session"
        browser_agent.sessions[session_id] = {
            "agent": AsyncMock(),
            "session_data": {
                "fields_filled": [
                    {"field": "phoneNumber", "value": "0901234567"}
                ]
            }
        }

        result = await browser_agent.read_field_value(field_name="phoneNumber", session_id=session_id)

        assert result["success"] is True
        assert result["value"] == "0901234567"

    @pytest.mark.asyncio
    async def test_read_field_value_missing(self, browser_agent):
        session_id = "missing-read"
        browser_agent.sessions[session_id] = {
            "agent": AsyncMock(),
            "session_data": {
                "fields_filled": []
            }
        }

        result = await browser_agent.read_field_value(field_name="email", session_id=session_id)

        assert result["success"] is False
        assert "Chưa có" in result["message"]

    @pytest.mark.asyncio
    async def test_upsert_field_incremental(self, browser_agent):
        """Test upserting a field (update or insert)"""
        session_id = "test-session-123"
        field_name = "customerName"
        
        # Setup session with existing field
        mock_agent = AsyncMock()
        mock_agent.add_new_task = Mock()
        mock_agent.run = AsyncMock()
        
        browser_agent.sessions[session_id] = {
            "agent": mock_agent,
            "session_data": {
                "fields_filled": [
                    {"field": field_name, "value": "Old Name"}
                ]
            }
        }
        
        # Update field
        new_value = "New Name"
        result = await browser_agent.upsert_field_incremental(
            field_name=field_name,
            value=new_value,
            session_id=session_id
        )
        
        assert result["success"] is True
        assert result["value"] == new_value
        # Check that value was updated
        filled_fields = browser_agent.sessions[session_id]["session_data"]["fields_filled"]
        assert any(f["field"] == field_name and f["value"] == new_value for f in filled_fields)

    @pytest.mark.asyncio
    async def test_remove_field_incremental(self, browser_agent):
        """Test removing a field"""
        session_id = "test-session-123"
        field_name = "customerName"
        
        # Setup session
        mock_agent = AsyncMock()
        mock_agent.add_new_task = Mock()
        mock_agent.run = AsyncMock()
        
        browser_agent.sessions[session_id] = {
            "agent": mock_agent,
            "session_data": {
                "fields_filled": [
                    {"field": field_name, "value": "Test Name"},
                    {"field": "phoneNumber", "value": "0901234567"}
                ]
            }
        }
        
        result = await browser_agent.remove_field_incremental(
            field_name=field_name,
            session_id=session_id
        )
        
        assert result["success"] is True
        # Check that field was removed
        filled_fields = browser_agent.sessions[session_id]["session_data"]["fields_filled"]
        assert not any(f["field"] == field_name for f in filled_fields)
        assert len(filled_fields) == 1

    @pytest.mark.asyncio
    async def test_clear_all_fields_incremental(self, browser_agent):
        """Test clearing all fields"""
        session_id = "test-session-123"
        
        # Setup session with filled fields
        mock_agent = AsyncMock()
        mock_agent.add_new_task = Mock()
        mock_agent.run = AsyncMock()
        
        browser_agent.sessions[session_id] = {
            "agent": mock_agent,
            "session_data": {
                "fields_filled": [
                    {"field": "customerName", "value": "Test"},
                    {"field": "phoneNumber", "value": "0901234567"}
                ]
            }
        }
        
        result = await browser_agent.clear_all_fields_incremental(session_id=session_id)
        
        assert result["success"] is True
        assert len(browser_agent.sessions[session_id]["session_data"]["fields_filled"]) == 0

    def test_get_filled_fields_success(self, browser_agent):
        """Test getting filled fields"""
        session_id = "test-session-123"
        
        browser_agent.sessions[session_id] = {
            "agent": AsyncMock(),
            "session_data": {
                "fields_filled": [
                    {"field": "customerName", "value": "Test"},
                    {"field": "phoneNumber", "value": "0901234567"}
                ]
            }
        }
        
        result = browser_agent.get_filled_fields(session_id=session_id)
        
        assert result["success"] is True
        assert len(result["fields"]) == 2

    def test_get_filled_fields_no_session(self, browser_agent):
        """Test getting filled fields for nonexistent session"""
        result = browser_agent.get_filled_fields(session_id="nonexistent")
        
        assert result["success"] is False
        assert "No active session" in result["error"]

    @pytest.mark.asyncio
    async def test_submit_form_incremental_success(self, browser_agent):
        """Test submitting form"""
        session_id = "test-session-123"
        
        # Setup session
        mock_agent = AsyncMock()
        mock_agent.add_new_task = Mock()
        mock_agent.run = AsyncMock()
        
        browser_agent.sessions[session_id] = {
            "agent": mock_agent,
            "session_data": {
                "type": "loan",
                "fields_filled": []
            }
        }
        
        with patch.object(browser_agent, '_close_session', return_value=None):
            result = await browser_agent.submit_form_incremental(session_id=session_id)
            
            assert result["success"] is True
            assert "submitted" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_execute_freeform_success(self, browser_agent, mock_browser, sample_form_data):
        """Test freeform execution"""
        user_message = "Điền đơn vay cho khách hàng Nguyen Van An, SĐT 0901234567"
        session_id = "test-session-123"
        
        with patch.object(browser_agent, '_get_llm', return_value=Mock()):
            with patch.object(browser_agent, '_ensure_browser', return_value=mock_browser):
                with patch('src.browser_agent.BrowserUseAgent') as mock_agent_class:
                    # Mock agent
                    mock_agent = AsyncMock()
                    mock_agent.run = AsyncMock(return_value="Form filled successfully")
                    mock_agent_class.return_value = mock_agent
                    
                    result = await browser_agent.execute_freeform(
                        user_message=user_message,
                        session_id=session_id
                    )
                    
                    assert result["success"] is True
                    assert "result" in result

    @pytest.mark.asyncio
    async def test_execute_freeform_no_result(self, browser_agent, mock_browser):
        """Test freeform execution with no result"""
        with patch.object(browser_agent, '_get_llm', return_value=Mock()):
            with patch.object(browser_agent, '_ensure_browser', return_value=mock_browser):
                with patch('src.browser_agent.BrowserUseAgent') as mock_agent_class:
                    # Mock agent returning None
                    mock_agent = AsyncMock()
                    mock_agent.run = AsyncMock(return_value=None)
                    mock_agent_class.return_value = mock_agent
                    
                    result = await browser_agent.execute_freeform(
                        user_message="Test message",
                        session_id="test-123"
                    )
                    
                    assert result["success"] is True
                    assert result["result"] == ""

    @pytest.mark.asyncio
    async def test_execute_freeform_error_handling(self, browser_agent, mock_browser):
        """Test freeform execution error handling"""
        with patch.object(browser_agent, '_get_llm', return_value=Mock()):
            with patch.object(browser_agent, '_ensure_browser', return_value=mock_browser):
                with patch('src.browser_agent.BrowserUseAgent') as mock_agent_class:
                    # Mock agent raising exception
                    mock_agent = AsyncMock()
                    mock_agent.run = AsyncMock(side_effect=Exception("Test error"))
                    mock_agent_class.return_value = mock_agent
                    
                    result = await browser_agent.execute_freeform(
                        user_message="Test message",
                        session_id="test-123"
                    )
                    
                    assert result["success"] is False
                    assert "error" in result

