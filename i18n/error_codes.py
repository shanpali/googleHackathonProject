"""
Error codes for the application.
These codes are used to map to localized error messages.
"""

class ErrorCodes:
    # Authentication errors (1000-1099)
    AUTH_MISSING_BEARER_TOKEN = "AUTH_001"
    AUTH_INVALID_TOKEN = "AUTH_002"
    
    # Validation errors (2000-2099)
    VALIDATION_MISSING_REQUIRED_FIELDS = "VAL_001"
    VALIDATION_INVALID_MCP_SERVER = "VAL_002"
    VALIDATION_INVALID_PROMPT = "VAL_003"
    
    # Server errors (5000-5099)
    SERVER_FINANCIAL_DATA_ERROR = "SRV_001"
    SERVER_PROCESSING_ERROR = "SRV_002"
    SERVER_MCP_CONNECTION_ERROR = "SRV_003"
