"""
Pytest Configuration and Fixtures
Shared fixtures for all tests
"""
import os
import sys
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load test environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.test'), override=True)


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing"""
    env_vars = {
        "AWS_ACCESS_KEY_ID": "test_aws_key",
        "AWS_SECRET_ACCESS_KEY": "test_aws_secret",
        "AWS_REGION": "us-east-1",
        "BEDROCK_MODEL_ID": "test-model",
        "OPENAI_API_KEY": "test_openai_key",
        "ELEVENLABS_API_KEY": "test_elevenlabs_key",
        "ELEVENLABS_VOICE_ID": "test_voice_id",
        "BROWSER_SERVICE_URL": "http://localhost:7863",
        "COGNITO_USER_POOL_ID": "test_pool_id",
        "COGNITO_CLIENT_ID": "test_client_id",
        "DYNAMODB_TABLE_NAME": "test-sessions",
        "DYNAMODB_REGION": "us-east-1",
    }
    
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    
    return env_vars


@pytest.fixture
def mock_dynamodb_client():
    """Mock boto3 DynamoDB client"""
    mock_client = MagicMock()
    mock_table = MagicMock()
    
    # Mock table operations
    mock_table.put_item = MagicMock(return_value={})
    mock_table.get_item = MagicMock(return_value={
        "Item": {
            "session_id": "test-session-123",
            "started_at": "2025-01-01T00:00:00Z",
            "messages": [],
            "workflow_executions": []
        }
    })
    mock_table.scan = MagicMock(return_value={
        "Items": [],
        "Count": 0
    })
    mock_table.load = MagicMock()
    
    mock_client.Table = MagicMock(return_value=mock_table)
    
    return mock_client


@pytest.fixture
def mock_cognito_client():
    """Mock boto3 Cognito client"""
    mock_client = MagicMock()
    
    # Mock authentication response
    mock_client.initiate_auth = MagicMock(return_value={
        "AuthenticationResult": {
            "AccessToken": "test_access_token",
            "IdToken": "test_id_token",
            "RefreshToken": "test_refresh_token",
            "ExpiresIn": 3600
        }
    })
    
    # Mock user verification
    mock_client.get_user = MagicMock(return_value={
        "Username": "testuser",
        "UserAttributes": [
            {"Name": "email", "Value": "test@example.com"},
            {"Name": "name", "Value": "Test User"}
        ]
    })
    
    return mock_client


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for browser automation"""
    mock_client = AsyncMock()
    
    # Mock chat completion
    mock_completion = AsyncMock()
    mock_completion.choices = [
        Mock(message=Mock(content="Success: Form filled successfully"))
    ]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
    
    return mock_client


@pytest.fixture
def mock_browser():
    """Mock Playwright browser"""
    mock_browser = AsyncMock()
    mock_page = AsyncMock()
    mock_context = AsyncMock()
    
    # Setup page mock
    mock_page.goto = AsyncMock()
    mock_page.fill = AsyncMock()
    mock_page.click = AsyncMock()
    mock_page.wait_for_selector = AsyncMock()
    mock_page.locator = MagicMock(return_value=AsyncMock())
    
    # Setup context mock
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    
    return mock_browser


@pytest.fixture
def sample_session_data():
    """Sample session data for testing"""
    return {
        "session_id": "test-session-123",
        "started_at": "2025-01-01T00:00:00Z",
        "messages": [
            {
                "role": "user",
                "content": "Tôi muốn vay 500 triệu",
                "timestamp": "2025-01-01T00:00:10Z"
            },
            {
                "role": "assistant",
                "content": "Dạ, tôi đã ghi nhận. Đang xử lý...",
                "timestamp": "2025-01-01T00:00:15Z"
            }
        ],
        "workflow_executions": []
    }


@pytest.fixture
def sample_form_data():
    """Sample form data for testing"""
    return {
        "customerName": "Nguyen Van An",
        "customerId": "012345678901",
        "phoneNumber": "0901234567",
        "email": "test@example.com",
        "dateOfBirth": "15/03/1985",
        "address": "123 Le Loi, District 1, HCMC",
        "loanAmount": "500000000",
        "loanTerm": "24",
        "loanPurpose": "Mua nhà",
        "occupation": "Kỹ sư phần mềm",
        "company": "FPT Software",
        "monthlyIncome": "30000000"
    }


@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp ClientSession"""
    mock_session = MagicMock()
    mock_response = MagicMock()
    
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "success": True,
        "result": "Form filled successfully"
    })
    mock_response.text = AsyncMock(return_value="Success")
    
    post_context_manager = MagicMock()
    post_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
    post_context_manager.__aexit__ = AsyncMock(return_value=None)
    mock_session.post = MagicMock(return_value=post_context_manager)
    
    get_context_manager = MagicMock()
    get_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
    get_context_manager.__aexit__ = AsyncMock(return_value=None)
    mock_session.get = MagicMock(return_value=get_context_manager)
    
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    
    return mock_session


@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    return Mock()

