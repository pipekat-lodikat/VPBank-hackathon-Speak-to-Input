"""
LangGraph State Definition - Compatible with Supervisor Pattern
Sử dụng MessagesState (built-in) kết hợp với custom fields
Ref: https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/
"""
from typing import TypedDict, Literal, Optional, Dict, List, Any, Annotated
from datetime import datetime
from operator import add
from langgraph.graph import MessagesState

# Intent types cho 5 use cases
IntentType = Literal["LOAN", "CRM", "HR", "COMPLIANCE", "OPERATIONS", "UNKNOWN"]

# Form types
FormType = Literal["loan", "crm", "hr", "compliance", "operations"]

# Execution status
ExecutionStatus = Literal["pending", "success", "failed", "validation_error"]


class MultiAgentState(MessagesState):
    """
    Extended MessagesState với custom fields cho multi-agent workflow.
    
    Kế thừa từ MessagesState để có:
    - messages: List[BaseMessage] - lịch sử conversation
    - Tự động reducer cho messages list
    
    Thêm custom fields cho:
    - Data extraction
    - Validation
    - Browser execution
    - Metadata
    """
    
    # ===== DATA EXTRACTION (Specialist Agents) =====
    extracted_data: Dict[str, Any]         # Extracted fields {field_name: value}
    
    # ===== VALIDATION =====
    is_valid: bool                         # Whether extracted data passes validation
    validation_errors: Annotated[List[str], add]  # Accumulated validation errors
    
    # ===== BROWSER EXECUTION (Browser Executor) =====
    form_url: str                          # URL of the form to fill
    form_type: FormType                    # Type of form: loan/crm/hr/compliance/operations
    browser_actions: List[Dict[str, Any]]  # Actions for browser executor
    execution_status: ExecutionStatus      # Status: pending/success/failed
    execution_result: Optional[str]        # Result message from browser execution
    
    # ===== METADATA =====
    session_id: str                        # Unique session identifier
    timestamp: datetime                    # When the request started
    current_agent: str                     # Name of agent currently processing
    
    # ===== ERROR HANDLING =====
    errors: Annotated[List[str], add]      # Accumulated errors


# Backward compatibility - alias SharedContext
SharedContext = MultiAgentState


def create_initial_state(user_message: str, session_id: str) -> MultiAgentState:
    """
    Helper function to create initial state for new workflow execution
    
    Args:
        user_message: User's voice input
        session_id: Unique session ID
        
    Returns:
        MultiAgentState with initial values
    """
    from langchain_core.messages import HumanMessage
    
    return {
        # MessagesState fields
        "messages": [HumanMessage(content=user_message)],
        
        # Data extraction
        "extracted_data": {},
        
        # Validation
        "is_valid": False,
        "validation_errors": [],
        
        # Browser execution
        "form_url": "",
        "form_type": "loan",
        "browser_actions": [],
        "execution_status": "pending",
        "execution_result": None,
        
        # Metadata
        "session_id": session_id,
        "timestamp": datetime.now(),
        "current_agent": "",
        
        # Error handling
        "errors": []
    }
