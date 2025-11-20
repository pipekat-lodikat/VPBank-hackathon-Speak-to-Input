"""
Unit Tests for AWS Cognito Authentication Service
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from botocore.exceptions import ClientError
from src.auth_service import CognitoAuthService


class TestCognitoAuthService:
    """Test suite for CognitoAuthService"""

    @pytest.fixture
    def mock_cognito_client_patch(self, mock_cognito_client):
        """Patch boto3 Cognito client"""
        with patch('src.auth_service.boto3.client') as mock_client:
            mock_client.return_value = mock_cognito_client
            yield mock_client

    @pytest.fixture
    def auth_service(self, mock_env_vars, mock_cognito_client_patch):
        """Create CognitoAuthService instance for testing"""
        return CognitoAuthService()

    def test_initialization(self, auth_service, mock_env_vars):
        """Test CognitoAuthService initialization"""
        assert auth_service.user_pool_id == mock_env_vars["COGNITO_USER_POOL_ID"]
        assert auth_service.client_id == mock_env_vars["COGNITO_CLIENT_ID"]
        assert auth_service.client is not None

    @pytest.mark.asyncio
    async def test_login_success(self, auth_service):
        """Test successful login"""
        username = "testuser"
        password = "testpass123"
        
        result = await auth_service.login(username, password)
        
        assert result["success"] is True
        assert "access_token" in result
        assert "id_token" in result
        assert "refresh_token" in result
        assert "expires_in" in result
        
        auth_service.client.initiate_auth.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, auth_service):
        """Test login with invalid credentials"""
        auth_service.client.initiate_auth.side_effect = ClientError(
            {
                'Error': {
                    'Code': 'NotAuthorizedException',
                    'Message': 'Incorrect username or password'
                }
            },
            'InitiateAuth'
        )
        
        result = await auth_service.login("testuser", "wrongpass")
        
        assert result["success"] is False
        assert result["error"] == "NotAuthorizedException"
        assert "password" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, auth_service):
        """Test login with non-existent user"""
        auth_service.client.initiate_auth.side_effect = ClientError(
            {
                'Error': {
                    'Code': 'UserNotFoundException',
                    'Message': 'User does not exist'
                }
            },
            'InitiateAuth'
        )
        
        result = await auth_service.login("nonexistent", "password")
        
        assert result["success"] is False
        assert result["error"] == "UserNotFoundException"

    @pytest.mark.asyncio
    async def test_verify_token_success(self, auth_service):
        """Test successful token verification"""
        access_token = "valid_token"
        
        result = await auth_service.verify_token(access_token)
        
        assert result is not None
        assert "username" in result
        assert "attributes" in result
        assert result["username"] == "testuser"
        
        auth_service.client.get_user.assert_called_once_with(AccessToken=access_token)

    @pytest.mark.asyncio
    async def test_verify_token_expired(self, auth_service):
        """Test token verification with expired token"""
        auth_service.client.get_user.side_effect = ClientError(
            {
                'Error': {
                    'Code': 'NotAuthorizedException',
                    'Message': 'Access Token has expired'
                }
            },
            'GetUser'
        )
        
        result = await auth_service.verify_token("expired_token")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_verify_token_invalid(self, auth_service):
        """Test token verification with invalid token"""
        auth_service.client.get_user.side_effect = ClientError(
            {
                'Error': {
                    'Code': 'NotAuthorizedException',
                    'Message': 'Invalid Access Token'
                }
            },
            'GetUser'
        )
        
        result = await auth_service.verify_token("invalid_token")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, auth_service):
        """Test successful token refresh"""
        refresh_token = "valid_refresh_token"
        
        result = await auth_service.refresh_token(refresh_token)
        
        assert result["success"] is True
        assert "access_token" in result
        assert "id_token" in result
        assert "expires_in" in result
        
        auth_service.client.initiate_auth.assert_called_once()

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, auth_service):
        """Test token refresh with invalid refresh token"""
        auth_service.client.initiate_auth.side_effect = ClientError(
            {
                'Error': {
                    'Code': 'NotAuthorizedException',
                    'Message': 'Refresh Token has expired'
                }
            },
            'InitiateAuth'
        )
        
        result = await auth_service.refresh_token("invalid_refresh_token")
        
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_register_user_success(self, auth_service):
        """Test successful user registration"""
        auth_service.client.admin_create_user = Mock()
        auth_service.client.admin_set_user_password = Mock()
        
        result = await auth_service.register_user(
            username="newuser",
            password="Password123!",
            email="newuser@example.com",
            phone_number="+84901234567",
            name="New User"
        )
        
        assert result["success"] is True
        assert "successfully" in result["message"].lower()
        
        auth_service.client.admin_create_user.assert_called_once()
        auth_service.client.admin_set_user_password.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_employee_role_blocked(self, auth_service):
        """Test that employee role registration is blocked"""
        result = await auth_service.register_user(
            username="employee",
            password="Password123!",
            email="employee@example.com",
            role="employee"
        )
        
        assert result["success"] is False
        assert result["error"] == "InvalidRole"
        assert "employee" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_register_user_username_exists(self, auth_service):
        """Test registration with existing username"""
        auth_service.client.admin_create_user.side_effect = ClientError(
            {
                'Error': {
                    'Code': 'UsernameExistsException',
                    'Message': 'User already exists'
                }
            },
            'AdminCreateUser'
        )
        
        result = await auth_service.register_user(
            username="existing",
            password="Password123!",
            email="existing@example.com"
        )
        
        assert result["success"] is False
        assert result["error"] == "UsernameExistsException"

    @pytest.mark.asyncio
    async def test_forgot_password_success(self, auth_service):
        """Test forgot password flow"""
        email = "test@example.com"
        
        # Mock finding username by email
        auth_service.client.list_users = Mock(return_value={
            "Users": [{"Username": "testuser"}]
        })
        auth_service.client.forgot_password = Mock()
        
        result = await auth_service.forgot_password(email)
        
        assert result["success"] is True
        assert "email" in result["message"].lower()
        
        auth_service.client.forgot_password.assert_called_once()

    @pytest.mark.asyncio
    async def test_forgot_password_user_not_found(self, auth_service):
        """Test forgot password with non-existent email"""
        auth_service.client.list_users = Mock(return_value={
            "Users": []
        })
        
        result = await auth_service.forgot_password("nonexistent@example.com")
        
        assert result["success"] is False
        assert result["error"] == "UserNotFoundException"

    @pytest.mark.asyncio
    async def test_reset_password_success(self, auth_service):
        """Test password reset with verification code"""
        email = "test@example.com"
        code = "123456"
        new_password = "NewPassword123!"
        
        # Mock finding username by email
        auth_service.client.list_users = Mock(return_value={
            "Users": [{"Username": "testuser"}]
        })
        auth_service.client.confirm_forgot_password = Mock()
        
        result = await auth_service.reset_password(email, code, new_password)
        
        assert result["success"] is True
        assert "thành công" in result["message"].lower()
        
        auth_service.client.confirm_forgot_password.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_password_invalid_code(self, auth_service):
        """Test password reset with invalid verification code"""
        auth_service.client.list_users = Mock(return_value={
            "Users": [{"Username": "testuser"}]
        })
        auth_service.client.confirm_forgot_password.side_effect = ClientError(
            {
                'Error': {
                    'Code': 'CodeMismatchException',
                    'Message': 'Invalid verification code'
                }
            },
            'ConfirmForgotPassword'
        )
        
        result = await auth_service.reset_password("test@example.com", "wrong", "NewPass123!")
        
        assert result["success"] is False
        assert result["error"] == "CodeMismatchException"

    @pytest.mark.asyncio
    async def test_find_username_by_email_success(self, auth_service):
        """Test finding username by email"""
        email = "test@example.com"
        
        auth_service.client.list_users = Mock(return_value={
            "Users": [{"Username": "testuser"}]
        })
        
        username = await auth_service._find_username_by_email(email)
        
        assert username == "testuser"

    @pytest.mark.asyncio
    async def test_find_username_by_email_not_found(self, auth_service):
        """Test finding username with non-existent email"""
        auth_service.client.list_users = Mock(return_value={
            "Users": []
        })
        
        username = await auth_service._find_username_by_email("nonexistent@example.com")
        
        assert username is None

