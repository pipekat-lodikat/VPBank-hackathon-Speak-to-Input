"""
OpenAPI/Swagger Documentation Generator
Generates comprehensive API documentation for all services
"""
from aiohttp import web
from aiohttp_swagger3 import SwaggerDocs, SwaggerUiSettings
import yaml


# ==================== Voice Bot API Documentation ====================

VOICE_BOT_OPENAPI_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "VPBank Voice Bot API",
        "version": "1.0.0",
        "description": "Voice Bot Service for VPBank Voice Agent - WebRTC audio streaming, STT, TTS, and LLM processing",
        "contact": {
            "name": "Pipekat Lodikat Team",
            "url": "https://github.com/pipekat-lodikat/speak-to-input"
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    },
    "servers": [
        {
            "url": "http://localhost:7860",
            "description": "Local development server"
        },
        {
            "url": "https://voice.vpbank.com",
            "description": "Production server"
        }
    ],
    "tags": [
        {
            "name": "WebRTC",
            "description": "WebRTC signaling and connection management"
        },
        {
            "name": "Sessions",
            "description": "Voice session management and history"
        },
        {
            "name": "Authentication",
            "description": "User authentication via AWS Cognito"
        },
        {
            "name": "Health",
            "description": "Service health checks"
        }
    ],
    "paths": {
        "/health": {
            "get": {
                "tags": ["Health"],
                "summary": "Health check endpoint",
                "description": "Check if Voice Bot service is healthy",
                "responses": {
                    "200": {
                        "description": "Service is healthy",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "example": "healthy"},
                                        "service": {"type": "string", "example": "vpbank-voice-bot"},
                                        "version": {"type": "string", "example": "1.0.0"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/offer": {
            "post": {
                "tags": ["WebRTC"],
                "summary": "Handle WebRTC offer",
                "description": "Accept WebRTC offer from client and return answer for audio streaming",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["type", "sdp"],
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "enum": ["offer"],
                                        "description": "SDP type"
                                    },
                                    "sdp": {
                                        "type": "string",
                                        "description": "Session Description Protocol data"
                                    }
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "WebRTC answer",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["answer"]},
                                        "sdp": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid offer"
                    }
                }
            }
        },
        "/ws": {
            "get": {
                "tags": ["WebRTC"],
                "summary": "WebSocket endpoint for transcript streaming",
                "description": "Real-time transcript streaming via WebSocket",
                "responses": {
                    "101": {
                        "description": "Switching Protocols - WebSocket connection established"
                    }
                }
            }
        },
        "/api/sessions": {
            "get": {
                "tags": ["Sessions"],
                "summary": "List all voice sessions",
                "description": "Get list of voice sessions with pagination",
                "parameters": [
                    {
                        "name": "limit",
                        "in": "query",
                        "description": "Maximum number of sessions to return",
                        "schema": {"type": "integer", "default": 50}
                    },
                    {
                        "name": "last_key",
                        "in": "query",
                        "description": "Last evaluated key for pagination (JSON string)",
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "List of sessions",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "sessions": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/Session"}
                                        },
                                        "count": {"type": "integer"},
                                        "last_evaluated_key": {"type": "object"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/sessions/{session_id}": {
            "get": {
                "tags": ["Sessions"],
                "summary": "Get session details",
                "description": "Get detailed information about a specific voice session",
                "parameters": [
                    {
                        "name": "session_id",
                        "in": "path",
                        "required": True,
                        "description": "Session identifier",
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Session details",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "session": {"$ref": "#/components/schemas/Session"}
                                    }
                                }
                            }
                        }
                    },
                    "404": {
                        "description": "Session not found"
                    }
                }
            }
        },
        "/api/auth/login": {
            "post": {
                "tags": ["Authentication"],
                "summary": "User login",
                "description": "Authenticate user with username and password via AWS Cognito",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["username", "password"],
                                "properties": {
                                    "username": {"type": "string"},
                                    "password": {"type": "string", "format": "password"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Login successful",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "access_token": {"type": "string"},
                                        "id_token": {"type": "string"},
                                        "refresh_token": {"type": "string"},
                                        "expires_in": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "Invalid credentials"
                    }
                }
            }
        }
    },
    "components": {
        "schemas": {
            "Session": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "started_at": {"type": "string", "format": "date-time"},
                    "ended_at": {"type": "string", "format": "date-time"},
                    "messages": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/Message"}
                    },
                    "workflow_executions": {"type": "array", "items": {"type": "object"}}
                }
            },
            "Message": {
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "enum": ["user", "assistant"]
                    },
                    "content": {"type": "string"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            }
        },
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
    }
}


# ==================== Browser Agent API Documentation ====================

BROWSER_AGENT_OPENAPI_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "VPBank Browser Agent API",
        "version": "1.0.0",
        "description": "Browser Agent Service for AI-powered form filling automation",
        "contact": {
            "name": "Pipekat Lodikat Team",
            "url": "https://github.com/pipekat-lodikat/speak-to-input"
        }
    },
    "servers": [
        {
            "url": "http://localhost:7863",
            "description": "Local development server"
        }
    ],
    "tags": [
        {
            "name": "Automation",
            "description": "Browser automation and form filling"
        },
        {
            "name": "Health",
            "description": "Service health checks"
        }
    ],
    "paths": {
        "/api/health": {
            "get": {
                "tags": ["Health"],
                "summary": "Health check endpoint",
                "responses": {
                    "200": {
                        "description": "Service is healthy"
                    }
                }
            }
        },
        "/api/execute": {
            "post": {
                "tags": ["Automation"],
                "summary": "Execute browser automation workflow",
                "description": "Execute freeform browser automation based on natural language instructions",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["user_message"],
                                "properties": {
                                    "user_message": {
                                        "type": "string",
                                        "description": "Natural language instruction for form filling",
                                        "example": "Điền đơn vay cho khách hàng Nguyen Van An, SĐT 0901234567"
                                    },
                                    "session_id": {
                                        "type": "string",
                                        "description": "Session identifier"
                                    },
                                    "request_id": {
                                        "type": "string",
                                        "description": "Request correlation ID"
                                    }
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Workflow executed successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "result": {"type": "string"},
                                        "session_id": {"type": "string"},
                                        "request_id": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid request"
                    },
                    "500": {
                        "description": "Workflow execution failed"
                    }
                }
            }
        },
        "/api/live": {
            "get": {
                "tags": ["Automation"],
                "summary": "Get current browser live URL",
                "description": "Get the URL of the currently open browser page",
                "responses": {
                    "200": {
                        "description": "Live URL",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "live_url": {"type": "string", "nullable": True}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}


def setup_swagger_ui(app: web.Application, spec: dict, ui_path: str = "/docs"):
    """
    Setup Swagger UI for aiohttp application
    
    Args:
        app: aiohttp Application
        spec: OpenAPI specification dictionary
        ui_path: Path to serve Swagger UI (default: /docs)
    """
    # Configure Swagger UI settings
    swagger_ui_settings = SwaggerUiSettings(
        path=ui_path,
        layout="BaseLayout",
        deepLinking=True,
        displayOperationId=True,
        defaultModelsExpandDepth=1,
        defaultModelExpandDepth=1,
        displayRequestDuration=True,
        filter=True,
        showExtensions=True,
        showCommonExtensions=True,
    )
    
    # Setup Swagger docs
    swagger = SwaggerDocs(
        app,
        spec_file=spec,
        swagger_ui_settings=swagger_ui_settings,
        validate=True,
        request_key="swagger_spec"
    )
    
    swagger.setup()
    
    from loguru import logger
    logger.info(f"📚 API documentation available at {ui_path}")


def export_openapi_spec(spec: dict, output_file: str):
    """
    Export OpenAPI spec to YAML file
    
    Args:
        spec: OpenAPI specification dictionary
        output_file: Output file path
    """
    with open(output_file, 'w') as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False)
    
    from loguru import logger
    logger.info(f"📄 OpenAPI spec exported to {output_file}")

