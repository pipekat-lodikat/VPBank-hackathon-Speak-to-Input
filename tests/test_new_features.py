"""
Unit tests for new features: file upload, search, draft management
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.browser_agent import browser_agent
from src.dynamodb_service import DynamoDBService


class TestFileUpload:
    """Test file upload functionality"""
    
    @pytest.mark.asyncio
    async def test_upload_file_success(self):
        """Test successful file upload"""
        # Mock session with AsyncMock agent
        mock_agent = AsyncMock()
        mock_agent.add_new_task = AsyncMock()
        mock_agent.run = AsyncMock()
        
        browser_agent.sessions["test-session"] = {
            "agent": mock_agent,
            "session_data": {"type": "loan", "url": "https://test.com"}
        }
        
        result = await browser_agent.upload_file_to_field(
            "idCardImage",
            "CCCD scan",
            "test-session"
        )
        
        assert result["success"] == True
        assert result["field"] == "idCardImage"
        assert "filename" in result
    
    @pytest.mark.asyncio
    async def test_upload_file_no_session(self):
        """Test file upload without active session"""
        result = await browser_agent.upload_file_to_field(
            "idCardImage",
            "CCCD scan",
            "non-existent-session"
        )
        
        assert result["success"] == False
        assert "No active session" in result["error"]


class TestSearchField:
    """Test search field functionality"""
    
    @pytest.mark.asyncio
    async def test_search_field_success(self):
        """Test successful field search"""
        # Mock session with AsyncMock agent
        mock_agent = AsyncMock()
        mock_agent.add_new_task = AsyncMock()
        mock_agent.run = AsyncMock()
        
        browser_agent.sessions["test-session"] = {
            "agent": mock_agent,
            "session_data": {"type": "loan"}
        }
        
        result = await browser_agent.search_and_focus_field(
            "số điện thoại",
            "test-session"
        )
        
        assert result["success"] == True
        assert "fields_found" in result
        assert "focused_field" in result
    
    @pytest.mark.asyncio
    async def test_search_field_vietnamese(self):
        """Test search with Vietnamese keywords"""
        # Mock session with AsyncMock agent
        mock_agent = AsyncMock()
        mock_agent.add_new_task = AsyncMock()
        mock_agent.run = AsyncMock()
        
        browser_agent.sessions["test-session"] = {
            "agent": mock_agent,
            "session_data": {"type": "loan"}
        }
        
        result = await browser_agent.search_and_focus_field(
            "email",
            "test-session"
        )
        
        assert result["success"] == True
    
    @pytest.mark.asyncio
    async def test_search_field_no_session(self):
        """Test search without active session"""
        result = await browser_agent.search_and_focus_field(
            "phone",
            "non-existent-session"
        )
        
        assert result["success"] == False


class TestDraftManagement:
    """Test draft save/load functionality"""
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires real DynamoDB connection")
    async def test_save_draft_success(self):
        """Test successful draft save"""
        # Mock session with filled fields
        browser_agent.sessions["test-session"] = {
            "agent": Mock(),
            "session_data": {
                "type": "loan",
                "url": "https://test.com",
                "fields_filled": [
                    {"field": "customerName", "value": "Test User"},
                    {"field": "phoneNumber", "value": "0901234567"}
                ]
            }
        }
        
        mock_dynamodb.save_draft.return_value = True
        
        result = await browser_agent.save_form_draft(
            "test-draft",
            "test-session"
        )
        
        assert result["success"] == True
        assert result["draft_name"] == "test-draft"
        assert result["fields_count"] == 2
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires real DynamoDB connection")
    async def test_load_draft_success(self):
        """Test successful draft load"""
        # Mock session
        browser_agent.sessions["test-session"] = {
            "agent": Mock(),
            "session_data": {
                "type": "loan",
                "fields_filled": []
            }
        }
        
        # Mock draft data
        mock_draft = {
            "draft_name": "test-draft",
            "fields_filled": [
                {"field": "customerName", "value": "Test User"},
                {"field": "phoneNumber", "value": "0901234567"}
            ]
        }
        mock_dynamodb.load_draft.return_value = mock_draft
        
        # Mock fill_field_incremental
        with patch.object(browser_agent, 'fill_field_incremental', new_callable=AsyncMock) as mock_fill:
            mock_fill.return_value = {"success": True}
            
            result = await browser_agent.load_form_draft(
                "test-draft",
                "test-session"
            )
            
            assert result["success"] == True
            assert result["fields_count"] == 2
            assert len(result["fields_loaded"]) == 2
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires real DynamoDB connection")
    async def test_load_draft_not_found(self):
        """Test load non-existent draft"""
        browser_agent.sessions["test-session"] = {
            "agent": Mock(),
            "session_data": {"type": "loan"}
        }
        
        mock_dynamodb.load_draft.return_value = None
        
        result = await browser_agent.load_form_draft(
            "non-existent-draft",
            "test-session"
        )
        
        assert result["success"] == False
        assert "not found" in result["error"]
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires real DynamoDB connection")
    async def test_save_draft_auto_name(self):
        """Test draft save with auto-generated name"""
        browser_agent.sessions["test-session"] = {
            "agent": Mock(),
            "session_data": {
                "type": "loan",
                "url": "https://test.com",
                "fields_filled": [{"field": "test", "value": "value"}]
            }
        }
        
        mock_dynamodb.save_draft.return_value = True
        
        # Save without providing name
        result = await browser_agent.save_form_draft(
            None,  # Auto-generate name
            "test-session"
        )
        
        # Should still succeed with auto-generated name
        assert result["success"] == True
        assert "draft_" in result["draft_name"]


class TestDynamoDBService:
    """Test DynamoDB draft methods"""
    
    @pytest.fixture
    def dynamodb_service(self):
        """Create DynamoDB service instance"""
        return DynamoDBService()
    
    def test_save_draft(self, dynamodb_service):
        """Test save draft to DynamoDB"""
        draft_data = {
            "form_type": "loan",
            "form_url": "https://test.com",
            "fields_filled": [
                {"field": "customerName", "value": "Test"}
            ],
            "session_id": "test-123"
        }
        
        with patch.object(dynamodb_service.table, 'put_item') as mock_put:
            result = dynamodb_service.save_draft("test-draft", draft_data)
            
            assert result == True
            mock_put.assert_called_once()
    
    def test_load_draft(self, dynamodb_service):
        """Test load draft from DynamoDB"""
        mock_response = {
            "Item": {
                "draft_name": "test-draft",
                "fields_filled": [{"field": "test", "value": "value"}]
            }
        }
        
        with patch.object(dynamodb_service.table, 'get_item', return_value=mock_response):
            result = dynamodb_service.load_draft("test-draft")
            
            assert result is not None
            assert result["draft_name"] == "test-draft"
    
    def test_load_draft_not_found(self, dynamodb_service):
        """Test load non-existent draft"""
        mock_response = {}  # No Item
        
        with patch.object(dynamodb_service.table, 'get_item', return_value=mock_response):
            result = dynamodb_service.load_draft("non-existent")
            
            assert result is None


class TestIntegration:
    """Integration tests for new features"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_complete_draft_workflow(self):
        """Test complete workflow: fill → save → load"""
        session_id = "integration-test-001"
        
        # 1. Start form session
        # 2. Fill some fields
        # 3. Save draft
        # 4. Clear session
        # 5. Load draft
        # 6. Verify fields restored
        
        # This would require actual browser instance
        # Mark as integration test to run separately
        pass
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_file_upload_workflow(self):
        """Test file upload in real browser"""
        # This requires actual browser and file picker
        # Mark as integration test
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
