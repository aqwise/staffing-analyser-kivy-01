from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from .config import settings


class AnalyzeRequest(BaseModel):
    """Request for analysis - api_key from config"""
    query: str = Field(..., min_length=1, max_length=10000)
    api_key: Optional[str] = Field(
        default=None,
        description="Google API key (uses GOOGLE_API_KEY from .env if null)"
    )
    session_id: Optional[str] = Field(None, description="Optional session ID for context")
    user_id: str = Field(default="user", description="User identifier")

    @validator('api_key', pre=True, always=True)
    def set_api_key(cls, v):
        """Auto-load API key from config if not provided"""
        if v is None or v == "":
            if settings.google_api_key:
                return settings.google_api_key
            else:
                raise ValueError("GOOGLE_API_KEY not configured and not provided in request")
        return v


class AnalyzeResponse(BaseModel):
    """Analysis response"""
    result: str
    session_id: str
    status: str
    timestamp: Optional[str] = None
    query_length: Optional[int] = None
    events_count: Optional[int] = None
    error: Optional[str] = None
    session_auto_created: Optional[bool] = False


class SessionCreateRequest(BaseModel):
    """Create session request"""
    user_id: str = Field(default="user")


class SessionCreateResponse(BaseModel):
    """Create session response"""
    session_id: str
    user_id: str
    created_at: str


class SessionInfoResponse(BaseModel):
    """Session info response"""
    session_id: str
    user_id: str
    created_at: str
    requests_count: int


class HealthResponse(BaseModel):
    """Health check response"""
    active_sessions: int
    total_requests: int
    status: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    status: str = "error"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
