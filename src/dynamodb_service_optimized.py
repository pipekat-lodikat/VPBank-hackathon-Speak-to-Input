"""
Optimized DynamoDB Service with GSI Support
Uses Global Secondary Indexes for efficient queries
"""
import os
import boto3
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from botocore.exceptions import ClientError
from loguru import logger
from dotenv import load_dotenv

load_dotenv(override=True)


class OptimizedDynamoDBService:
    """Optimized DynamoDB service with GSI support"""
    
    def __init__(self):
        # Get credentials
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
        
        # Verify table exists
        try:
            self.table.load()
            logger.info(f"✅ DynamoDB table '{table_name}' ready with GSI support")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.error(f"❌ DynamoDB table '{table_name}' not found. Please create it first.")
            else:
                logger.error(f"❌ DynamoDB error: {e}")
    
    def save_session(
        self,
        session_data: Dict[str, Any],
        user_id: Optional[str] = None,
        status: str = "active"
    ) -> bool:
        """
        Save or update session with GSI attributes
        
        Args:
            session_data: Session data dictionary
            user_id: User ID (for GSI)
            status: Session status (active/completed/failed)
            
        Returns:
            True if successful
        """
        try:
            session_id = session_data.get("session_id")
            if not session_id:
                logger.error("❌ session_id is required")
                return False
            
            # Prepare item with GSI attributes
            item = {
                "session_id": session_id,
                "started_at": session_data.get("started_at", datetime.now(timezone.utc).isoformat()),
                "messages": session_data.get("messages", []),
                "workflow_executions": session_data.get("workflow_executions", []),
                "created_at": int(datetime.now(timezone.utc).timestamp()),
                "status": status,  # For GSI
            }
            
            # Add user_id if provided (for GSI)
            if user_id:
                item["user_id"] = user_id
            
            # Add ended_at if present
            if "ended_at" in session_data:
                item["ended_at"] = session_data["ended_at"]
                item["status"] = "completed"
            
            # TTL: 90 days
            item["ttl"] = int((datetime.now(timezone.utc).timestamp()) + (90 * 24 * 60 * 60))
            
            # Put item
            self.table.put_item(Item=item)
            logger.debug(f"💾 Saved session {session_id} to DynamoDB with GSI attributes")
            return True
            
        except ClientError as e:
            logger.error(f"❌ Failed to save session to DynamoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error saving session: {e}", exc_info=True)
            return False
    
    def get_sessions_by_user(
        self,
        user_id: str,
        limit: int = 50,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get sessions for a specific user using GSI
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            start_date: Filter sessions after this date
            end_date: Filter sessions before this date
            
        Returns:
            Dictionary with sessions and metadata
        """
        try:
            query_params = {
                "IndexName": "user_id-created_at-index",
                "KeyConditionExpression": "user_id = :user_id",
                "ExpressionAttributeValues": {":user_id": user_id},
                "ScanIndexForward": False,  # DESC order (newest first)
                "Limit": limit
            }
            
            # Add date range filter if provided
            if start_date or end_date:
                key_condition = "user_id = :user_id"
                if start_date and end_date:
                    key_condition += " AND created_at BETWEEN :start AND :end"
                    query_params["ExpressionAttributeValues"][":start"] = int(start_date.timestamp())
                    query_params["ExpressionAttributeValues"][":end"] = int(end_date.timestamp())
                elif start_date:
                    key_condition += " AND created_at >= :start"
                    query_params["ExpressionAttributeValues"][":start"] = int(start_date.timestamp())
                elif end_date:
                    key_condition += " AND created_at <= :end"
                    query_params["ExpressionAttributeValues"][":end"] = int(end_date.timestamp())
                
                query_params["KeyConditionExpression"] = key_condition
            
            response = self.table.query(**query_params)
            items = response.get("Items", [])
            
            logger.info(f"📋 Found {len(items)} sessions for user {user_id}")
            
            return {
                "items": items,
                "count": len(items),
                "last_evaluated_key": response.get("LastEvaluatedKey")
            }
            
        except ClientError as e:
            logger.error(f"❌ Failed to query sessions by user: {e}")
            return {"items": [], "count": 0, "last_evaluated_key": None}
    
    def get_sessions_by_status(
        self,
        status: str = "active",
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get sessions by status using GSI
        
        Args:
            status: Session status (active/completed/failed)
            limit: Maximum number of results
            
        Returns:
            Dictionary with sessions and metadata
        """
        try:
            response = self.table.query(
                IndexName="status-created_at-index",
                KeyConditionExpression="#status = :status",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={":status": status},
                ScanIndexForward=False,  # DESC order
                Limit=limit
            )
            
            items = response.get("Items", [])
            
            logger.info(f"📋 Found {len(items)} sessions with status '{status}'")
            
            return {
                "items": items,
                "count": len(items),
                "last_evaluated_key": response.get("LastEvaluatedKey")
            }
            
        except ClientError as e:
            logger.error(f"❌ Failed to query sessions by status: {e}")
            return {"items": [], "count": 0, "last_evaluated_key": None}
    
    def get_recent_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get most recent sessions across all users (optimized query)
        
        Args:
            limit: Maximum number of sessions
            
        Returns:
            List of recent sessions
        """
        try:
            # Use status GSI with 'active' or 'completed' status
            # This is faster than scanning entire table
            response = self.table.query(
                IndexName="status-created_at-index",
                KeyConditionExpression="#status IN (:active, :completed)",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":active": "active",
                    ":completed": "completed"
                },
                ScanIndexForward=False,
                Limit=limit
            )
            
            return response.get("Items", [])
            
        except ClientError as e:
            logger.error(f"❌ Failed to get recent sessions: {e}")
            return []
    
    def batch_get_sessions(self, session_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Batch get multiple sessions efficiently
        
        Args:
            session_ids: List of session IDs
            
        Returns:
            List of sessions
        """
        try:
            # DynamoDB batch_get_item supports up to 100 items
            if len(session_ids) > 100:
                logger.warning(f"⚠️  Batch size {len(session_ids)} exceeds 100, truncating")
                session_ids = session_ids[:100]
            
            keys = [{"session_id": sid} for sid in session_ids]
            
            response = self.dynamodb.batch_get_item(
                RequestItems={
                    self.table_name: {
                        "Keys": keys
                    }
                }
            )
            
            items = response.get("Responses", {}).get(self.table_name, [])
            logger.info(f"📦 Batch retrieved {len(items)} sessions")
            
            return items
            
        except ClientError as e:
            logger.error(f"❌ Failed to batch get sessions: {e}")
            return []
    
    def update_session_status(self, session_id: str, status: str) -> bool:
        """
        Update session status efficiently
        
        Args:
            session_id: Session ID
            status: New status
            
        Returns:
            True if successful
        """
        try:
            self.table.update_item(
                Key={"session_id": session_id},
                UpdateExpression="SET #status = :status",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={":status": status}
            )
            
            logger.info(f"✅ Updated session {session_id} status to '{status}'")
            return True
            
        except ClientError as e:
            logger.error(f"❌ Failed to update session status: {e}")
            return False

