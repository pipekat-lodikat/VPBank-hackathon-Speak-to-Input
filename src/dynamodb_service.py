"""
DynamoDB Service for Session History
Lưu trữ và quản lý session transcripts với credential riêng
"""
import os
import boto3
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from botocore.exceptions import ClientError
from loguru import logger
from dotenv import load_dotenv

load_dotenv(override=True)


class DynamoDBService:
    """Service quản lý DynamoDB với credential riêng"""
    
    def __init__(self):
        # Lấy credentials riêng cho DynamoDB
        access_key = os.getenv("DYNAMODB_ACCESS_KEY_ID")
        secret_key = os.getenv("DYNAMODB_SECRET_ACCESS_KEY")
        region = os.getenv("DYNAMODB_REGION", "us-east-1")
        table_name = os.getenv("DYNAMODB_TABLE_NAME", "vpbank-sessions")
        
        if not access_key or not secret_key:
            logger.warning("⚠️  DynamoDB credentials not found. Using default AWS credentials.")
            self.dynamodb = boto3.resource('dynamodb', region_name=region)
        else:
            logger.info(f"✅ Using separate DynamoDB credentials (region: {region})")
            self.dynamodb = boto3.resource(
                'dynamodb',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
        
        self.table_name = table_name
        self.table = self.dynamodb.Table(table_name)
        
        # Kiểm tra table tồn tại
        try:
            self.table.load()
            logger.info(f"✅ DynamoDB table '{table_name}' ready")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.error(f"❌ DynamoDB table '{table_name}' not found. Please create it first.")
            else:
                logger.error(f"❌ DynamoDB error: {e}")
    
    def save_session(self, session_data: Dict[str, Any]) -> bool:
        """
        Lưu hoặc cập nhật session vào DynamoDB
        
        Args:
            session_data: Dict chứa session_id, started_at, messages, etc.
            
        Returns:
            bool: True nếu thành công
        """
        try:
            session_id = session_data.get("session_id")
            if not session_id:
                logger.error("❌ session_id is required")
                return False
            
            # Chuẩn bị item cho DynamoDB
            item = {
                "session_id": session_id,
                "started_at": session_data.get("started_at", datetime.now(timezone.utc).isoformat()),
                "messages": session_data.get("messages", []),
                "workflow_executions": session_data.get("workflow_executions", []),
                "created_at": int(datetime.now(timezone.utc).timestamp()),
            }
            
            # Thêm ended_at nếu có
            if "ended_at" in session_data:
                item["ended_at"] = session_data["ended_at"]
            
            # TTL: 90 days từ khi tạo
            item["ttl"] = int((datetime.now(timezone.utc).timestamp()) + (90 * 24 * 60 * 60))
            
            # Put item (upsert)
            self.table.put_item(Item=item)
            logger.debug(f"💾 Saved session {session_id} to DynamoDB")
            return True
            
        except ClientError as e:
            logger.error(f"❌ Failed to save session to DynamoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error saving session: {e}", exc_info=True)
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy session theo session_id
        
        Args:
            session_id: Session ID cần lấy
            
        Returns:
            Dict session data hoặc None nếu không tìm thấy
        """
        try:
            response = self.table.get_item(
                Key={"session_id": session_id}
            )
            
            if "Item" in response:
                item = response["Item"]
                logger.debug(f"📖 Retrieved session {session_id} from DynamoDB")
                return item
            else:
                logger.debug(f"📭 Session {session_id} not found")
                return None
                
        except ClientError as e:
            logger.error(f"❌ Failed to get session from DynamoDB: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error getting session: {e}", exc_info=True)
            return None
    
    def list_sessions(self, limit: int = 50, last_key: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Lấy danh sách sessions (sorted by created_at DESC)
        
        Args:
            limit: Số lượng sessions tối đa
            last_key: LastEvaluatedKey cho pagination
            
        Returns:
            Dict chứa items và last_evaluated_key
        """
        try:
            # Scan table và sort by created_at DESC
            # Note: DynamoDB không hỗ trợ sort trực tiếp, cần scan rồi sort trong code
            scan_kwargs = {
                "Limit": limit * 2  # Lấy nhiều hơn để sort, rồi limit lại
            }
            
            if last_key:
                scan_kwargs["ExclusiveStartKey"] = last_key
            
            response = self.table.scan(**scan_kwargs)
            items = response.get("Items", [])
            
            # Sort by created_at DESC
            items.sort(key=lambda x: x.get("created_at", 0), reverse=True)
            
            # Limit kết quả
            items = items[:limit]
            
            result = {
                "items": items,
                "count": len(items),
                "last_evaluated_key": response.get("LastEvaluatedKey")
            }
            
            logger.debug(f"📋 Listed {len(items)} sessions from DynamoDB")
            return result
            
        except ClientError as e:
            logger.error(f"❌ Failed to list sessions from DynamoDB: {e}")
            return {"items": [], "count": 0, "last_evaluated_key": None}
        except Exception as e:
            logger.error(f"❌ Unexpected error listing sessions: {e}", exc_info=True)
            return {"items": [], "count": 0, "last_evaluated_key": None}
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """
        Cập nhật session (partial update)
        
        Args:
            session_id: Session ID cần cập nhật
            updates: Dict chứa các field cần update
            
        Returns:
            bool: True nếu thành công
        """
        try:
            # Build update expression
            update_expr_parts = []
            expr_attr_names = {}
            expr_attr_values = {}
            
            for key, value in updates.items():
                attr_name = f"#{key}"
                attr_value = f":{key}"
                update_expr_parts.append(f"{attr_name} = {attr_value}")
                expr_attr_names[attr_name] = key
                expr_attr_values[attr_value] = value
            
            update_expression = "SET " + ", ".join(update_expr_parts)
            
            self.table.update_item(
                Key={"session_id": session_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expr_attr_names,
                ExpressionAttributeValues=expr_attr_values
            )
            
            logger.debug(f"🔄 Updated session {session_id} in DynamoDB")
            return True
            
        except ClientError as e:
            logger.error(f"❌ Failed to update session in DynamoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error updating session: {e}", exc_info=True)
            return False


    def save_draft(self, draft_name: str, draft_data: dict) -> bool:
        """
        Save form draft to DynamoDB
        
        Args:
            draft_name: Unique name for the draft
            draft_data: Draft data including fields_filled, form_type, etc.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            item = {
                "session_id": f"draft_{draft_name}",  # Use draft_ prefix
                "draft_name": draft_name,
                "created_at": draft_data.get("created_at", datetime.now(timezone.utc).isoformat()),
                "status": "draft",
                "form_type": draft_data.get("form_type", "unknown"),
                "form_url": draft_data.get("form_url", ""),
                "fields_filled": draft_data.get("fields_filled", []),
                "session_id_original": draft_data.get("session_id", ""),
            }
            
            self.table.put_item(Item=item)
            logger.info(f"💾 Saved draft '{draft_name}' to DynamoDB")
            return True
            
        except ClientError as e:
            logger.error(f"❌ Failed to save draft: {e}")
            return False
    
    def load_draft(self, draft_name: str) -> Optional[dict]:
        """Load form draft from DynamoDB"""
        try:
            response = self.table.get_item(
                Key={"session_id": f"draft_{draft_name}"}
            )
            
            if "Item" in response:
                logger.info(f"📂 Loaded draft '{draft_name}'")
                return response["Item"]
            else:
                logger.warning(f"⚠️  Draft '{draft_name}' not found")
                return None
                
        except ClientError as e:
            logger.error(f"❌ Failed to load draft: {e}")
            return None
