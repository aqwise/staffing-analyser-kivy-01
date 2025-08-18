from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from .config import settings


class AnalyzeRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10000)
    api_key: Optional[str] = None
    session_id: Optional[str] = None
    user_id: str = "user"
    business_domain: Optional[str] = Field(
        None,
        description="Business domain: QA, AQA or DevOps (defaults to AQA if not specified)"
    )


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
    """Session info response with auto_created flag"""
    session_id: str
    user_id: str
    created_at: str
    requests_count: int
    auto_created: Optional[bool] = False


class HealthResponse(BaseModel):
    """Health check response with detailed session stats"""
    active_sessions: int
    persistent_sessions: Optional[int] = None
    auto_created_sessions: Optional[int] = None
    total_requests: int
    status: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    status: str = "error"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class SessionDeleteResponse(BaseModel):
    """Session deletion response"""
    success: bool
    session_id: str
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
