"""
AWS Cognito Authentication Service
"""
import os
import boto3
from botocore.exceptions import ClientError
from loguru import logger


class CognitoAuthService:
    def __init__(self):
        self.region = os.getenv("AWS_REGION", "ap-southeast-1")
        self.user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
        self.client_id = os.getenv("COGNITO_CLIENT_ID")

        logger.info(f"🔐 Cognito Config: Region={self.region}, Pool={self.user_pool_id}, Client={self.client_id}")

        if not self.user_pool_id or not self.client_id:
            logger.warning("⚠️  Cognito credentials not configured")

        auth_access_key = os.getenv("AUTH_AWS_ACCESS_KEY_ID")
        auth_secret_key = os.getenv("AUTH_AWS_SECRET_ACCESS_KEY")

        if auth_access_key and auth_secret_key:
            self.client = boto3.client(
                "cognito-idp",
                region_name=self.region,
                aws_access_key_id=auth_access_key,
                aws_secret_access_key=auth_secret_key,
            )
            logger.info(f"🔐 Using AUTH credentials: {auth_access_key[:8]}...")
        else:
            aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

            if aws_access_key and aws_secret_key:
                self.client = boto3.client(
                    "cognito-idp",
                    region_name=self.region,
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                )
                logger.info(f"🔐 Using main AWS credentials: {aws_access_key[:8]}...")
            else:
                self.client = boto3.client("cognito-idp", region_name=self.region)
                logger.warning("⚠️  Using default AWS credentials")

    async def login(self, username: str, password: str):
        """Authenticate user with Cognito"""
        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": username,
                    "PASSWORD": password,
                },
            )

            return {
                "success": True,
                "access_token": response["AuthenticationResult"]["AccessToken"],
                "id_token": response["AuthenticationResult"]["IdToken"],
                "refresh_token": response["AuthenticationResult"]["RefreshToken"],
                "expires_in": response["AuthenticationResult"]["ExpiresIn"],
            }
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(f"Cognito login error: {error_code} - {error_message}")

            return {
                "success": False,
                "error": error_code,
                "message": error_message,
            }
        except Exception as e:
            logger.error(f"Unexpected login error: {e}")
            return {
                "success": False,
                "error": "UnknownError",
                "message": str(e),
            }

    async def verify_token(self, access_token: str):
        """Verify access token"""
        try:
            response = self.client.get_user(AccessToken=access_token)
            return {
                "username": response["Username"],
                "attributes": {attr["Name"]: attr["Value"] for attr in response["UserAttributes"]},
            }
        except ClientError as e:
            logger.error(f"Token verification failed: {e}")
            return None

    async def refresh_token(self, refresh_token: str):
        """Refresh access token"""
        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow="REFRESH_TOKEN_AUTH",
                AuthParameters={
                    "REFRESH_TOKEN": refresh_token,
                },
            )

            return {
                "success": True,
                "access_token": response["AuthenticationResult"]["AccessToken"],
                "id_token": response["AuthenticationResult"]["IdToken"],
                "expires_in": response["AuthenticationResult"]["ExpiresIn"],
            }
        except ClientError as e:
            logger.error(f"Token refresh failed: {e}")
            return {"success": False, "error": str(e)}

    async def register_user(
        self,
        username: str,
        password: str,
        email: str,
        phone_number: str = None,
        name: str = None,
        role: str = "user",
    ):
        """Register new user with email"""
        if role == "employee":
            logger.warning(f"🚫 Attempted self-registration with employee role: {username}")
            return {
                "success": False,
                "error": "InvalidRole",
                "message": "Employee accounts cannot be self-registered. Please contact administrator.",
            }

        try:
            attributes = [
                {"Name": "email", "Value": email},
                {"Name": "email_verified", "Value": "true"},
            ]

            if phone_number:
                attributes.append({"Name": "phone_number", "Value": phone_number})
            if name:
                attributes.append({"Name": "name", "Value": name})

            attributes.append({"Name": "custom:role", "Value": role})

            self.client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=username,
                UserAttributes=attributes,
                TemporaryPassword=password,
                MessageAction="SUPPRESS",
            )

            self.client.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=username,
                Password=password,
                Permanent=True,
            )

            return {"success": True, "message": "User registered successfully"}

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(f"Registration error: {error_code} - {error_message}")

            return {
                "success": False,
                "error": error_code,
                "message": error_message,
            }

    async def forgot_password(self, email: str):
        """Initiate forgot password flow via email"""
        try:
            username = await self._find_username_by_email(email)
            if not username:
                return {
                    "success": False,
                    "error": "UserNotFoundException",
                    "message": "Email không tồn tại trong hệ thống",
                }

            self.client.forgot_password(
                ClientId=self.client_id,
                Username=username,
            )

            return {"success": True, "message": "Đã gửi mã xác thực đến email của bạn"}
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(f"Forgot password error: {error_code} - {error_message}")

            return {
                "success": False,
                "error": error_code,
                "message": error_message,
            }

    async def reset_password(self, email: str, code: str, new_password: str):
        """Confirm forgot password with verification code"""
        try:
            username = await self._find_username_by_email(email)
            if not username:
                return {
                    "success": False,
                    "error": "UserNotFoundException",
                    "message": "Email không tồn tại trong hệ thống",
                }

            self.client.confirm_forgot_password(
                ClientId=self.client_id,
                Username=username,
                ConfirmationCode=code,
                Password=new_password,
            )

            return {"success": True, "message": "Đổi mật khẩu thành công"}
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(f"Reset password error: {error_code} - {error_message}")

            return {
                "success": False,
                "error": error_code,
                "message": error_message,
            }

    async def _find_username_by_email(self, email: str):
        """Helper to find username by email using Cognito list_users"""
        try:
            response = self.client.list_users(
                UserPoolId=self.user_pool_id,
                Filter=f'email = "{email}"',
                Limit=1,
            )

            users = response.get("Users", [])
            if users:
                return users[0]["Username"]
            return None
        except ClientError as e:
            logger.error(f"Error finding username by email: {e}")
            return None
