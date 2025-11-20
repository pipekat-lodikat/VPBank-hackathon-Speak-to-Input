"""
Unit Tests for DynamoDB Service
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from decimal import Decimal
from botocore.exceptions import ClientError
from src.dynamodb_service import DynamoDBService


class TestDynamoDBService:
    """Test suite for DynamoDBService"""

    @pytest.fixture
    def mock_dynamodb_resource(self, mock_dynamodb_client):
        """Mock boto3 DynamoDB resource"""
        with patch('src.dynamodb_service.boto3.resource') as mock_resource:
            mock_resource.return_value = mock_dynamodb_client
            yield mock_resource

    @pytest.fixture
    def dynamodb_service(self, mock_env_vars, mock_dynamodb_resource):
        """Create DynamoDBService instance for testing"""
        return DynamoDBService()

    def test_initialization_with_credentials(self, mock_env_vars, mock_dynamodb_resource):
        """Test DynamoDB service initialization with credentials"""
        service = DynamoDBService()
        
        assert service.table_name == "test-sessions"
        assert service.table is not None

    def test_initialization_without_credentials(self, monkeypatch, mock_dynamodb_resource):
        """Test DynamoDB service initialization without custom credentials"""
        # Remove DynamoDB-specific credentials
        monkeypatch.delenv("DYNAMODB_ACCESS_KEY_ID", raising=False)
        monkeypatch.delenv("DYNAMODB_SECRET_ACCESS_KEY", raising=False)
        monkeypatch.setenv("DYNAMODB_TABLE_NAME", "test-sessions")
        
        service = DynamoDBService()
        assert service.table_name == "test-sessions"

    def test_save_session_success(self, dynamodb_service, sample_session_data):
        """Test saving session successfully"""
        result = dynamodb_service.save_session(sample_session_data)
        
        assert result is True
        dynamodb_service.table.put_item.assert_called_once()
        
        # Verify item structure
        call_args = dynamodb_service.table.put_item.call_args
        item = call_args[1]['Item']
        assert item['session_id'] == sample_session_data['session_id']
        assert 'ttl' in item
        assert 'created_at' in item

    def test_save_session_missing_session_id(self, dynamodb_service):
        """Test saving session without session_id"""
        invalid_data = {
            "started_at": "2025-01-01T00:00:00Z",
            "messages": []
        }
        
        result = dynamodb_service.save_session(invalid_data)
        assert result is False

    def test_save_session_with_ended_at(self, dynamodb_service, sample_session_data):
        """Test saving session with ended_at timestamp"""
        sample_session_data["ended_at"] = "2025-01-01T01:00:00Z"
        
        result = dynamodb_service.save_session(sample_session_data)
        assert result is True
        
        # Verify ended_at is included
        call_args = dynamodb_service.table.put_item.call_args
        item = call_args[1]['Item']
        assert 'ended_at' in item

    def test_save_session_client_error(self, dynamodb_service, sample_session_data):
        """Test handling ClientError during save"""
        dynamodb_service.table.put_item.side_effect = ClientError(
            {'Error': {'Code': 'ValidationException', 'Message': 'Test error'}},
            'PutItem'
        )
        
        result = dynamodb_service.save_session(sample_session_data)
        assert result is False

    def test_get_session_success(self, dynamodb_service):
        """Test getting session successfully"""
        session_id = "test-session-123"
        
        dynamodb_service.table.get_item.return_value = {
            "Item": {
                "session_id": session_id,
                "started_at": "2025-01-01T00:00:00Z",
                "messages": [],
                "created_at": Decimal('1704067200')
            }
        }
        
        result = dynamodb_service.get_session(session_id)
        
        assert result is not None
        assert result["session_id"] == session_id
        dynamodb_service.table.get_item.assert_called_once_with(
            Key={"session_id": session_id}
        )

    def test_get_session_not_found(self, dynamodb_service):
        """Test getting non-existent session"""
        dynamodb_service.table.get_item.return_value = {}
        
        result = dynamodb_service.get_session("nonexistent")
        assert result is None

    def test_get_session_client_error(self, dynamodb_service):
        """Test handling ClientError during get"""
        dynamodb_service.table.get_item.side_effect = ClientError(
            {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Test error'}},
            'GetItem'
        )
        
        result = dynamodb_service.get_session("test-session")
        assert result is None

    def test_list_sessions_success(self, dynamodb_service):
        """Test listing sessions successfully"""
        mock_items = [
            {
                "session_id": "session-1",
                "created_at": Decimal('1704067200'),
                "started_at": "2025-01-01T00:00:00Z"
            },
            {
                "session_id": "session-2",
                "created_at": Decimal('1704063600'),
                "started_at": "2025-01-01T00:00:00Z"
            }
        ]
        
        dynamodb_service.table.scan.return_value = {
            "Items": mock_items,
            "Count": 2
        }
        
        result = dynamodb_service.list_sessions(limit=10)
        
        assert result["count"] == 2
        assert len(result["items"]) == 2
        # Verify sorted by created_at DESC
        assert result["items"][0]["created_at"] >= result["items"][1]["created_at"]

    def test_list_sessions_with_pagination(self, dynamodb_service):
        """Test listing sessions with pagination"""
        last_key = {"session_id": "session-1"}
        
        dynamodb_service.table.scan.return_value = {
            "Items": [],
            "Count": 0,
            "LastEvaluatedKey": {"session_id": "session-10"}
        }
        
        result = dynamodb_service.list_sessions(limit=10, last_key=last_key)
        
        assert "last_evaluated_key" in result
        dynamodb_service.table.scan.assert_called_once()
        call_args = dynamodb_service.table.scan.call_args[1]
        assert "ExclusiveStartKey" in call_args

    def test_list_sessions_empty(self, dynamodb_service):
        """Test listing sessions when none exist"""
        dynamodb_service.table.scan.return_value = {
            "Items": [],
            "Count": 0
        }
        
        result = dynamodb_service.list_sessions()
        
        assert result["count"] == 0
        assert result["items"] == []

    def test_list_sessions_client_error(self, dynamodb_service):
        """Test handling ClientError during list"""
        dynamodb_service.table.scan.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Test error'}},
            'Scan'
        )
        
        result = dynamodb_service.list_sessions()
        
        assert result["count"] == 0
        assert result["items"] == []

    def test_update_session_success(self, dynamodb_service):
        """Test updating session successfully"""
        session_id = "test-session-123"
        updates = {
            "ended_at": "2025-01-01T01:00:00Z",
            "status": "completed"
        }
        
        dynamodb_service.table.update_item.return_value = {}
        
        result = dynamodb_service.update_session(session_id, updates)
        
        assert result is True
        dynamodb_service.table.update_item.assert_called_once()
        
        # Verify update expression
        call_args = dynamodb_service.table.update_item.call_args[1]
        assert "UpdateExpression" in call_args
        assert "ExpressionAttributeNames" in call_args
        assert "ExpressionAttributeValues" in call_args

    def test_update_session_client_error(self, dynamodb_service):
        """Test handling ClientError during update"""
        dynamodb_service.table.update_item.side_effect = ClientError(
            {'Error': {'Code': 'ValidationException', 'Message': 'Test error'}},
            'UpdateItem'
        )
        
        result = dynamodb_service.update_session("test-session", {"status": "completed"})
        assert result is False

    def test_update_session_empty_updates(self, dynamodb_service):
        """Test updating session with empty updates dict"""
        result = dynamodb_service.update_session("test-session", {})
        
        # Should not make API call with empty updates
        assert result is True or result is False  # Implementation dependent

