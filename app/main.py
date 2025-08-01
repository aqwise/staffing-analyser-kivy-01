import sys
from datetime import datetime  # ← ДОБАВЛЕН ИМПОРТ
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from .config import settings
from .models import (
    AnalyzeRequest, AnalyzeResponse,
    SessionCreateRequest, SessionCreateResponse,
    SessionInfoResponse, HealthResponse, ErrorResponse
)
from .services import analysis_service

# Configure logging
logger.remove()
logger.add(sys.stdout, level=settings.log_level, format="{time} | {level} | {message}")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Staffing request analysis API - session_id optional",
    debug=settings.debug
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(error="Internal server error").dict()
    )


# Root endpoint
@app.get("/")
async def root():
    """API information"""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "status": "running",
        "docs": "/docs",
        "note": "session_id is optional in /api/v1/analyze",
        "endpoints": {
            "analyze": "POST /api/v1/analyze (session_id optional)",
            "sessions": "POST /api/v1/sessions",
            "health": "GET /health"
        }
    }


# Health check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """System health check"""
    logger.info("Health check requested")
    health_info = analysis_service.health_check()

    return HealthResponse(
        active_sessions=health_info["active_sessions"],
        total_requests=health_info["total_requests"],
        status=health_info["status"]
    )


# Main analysis endpoint - session_id optional
@app.post("/api/v1/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """
    Analyze staffing request text

    session_id is OPTIONAL:
    - If provided: uses existing session context
    - If not provided: auto-creates temporary session for this request
    """
    session_note = f"session: {request.session_id or 'auto-create'}"
    logger.info(f"Analysis request - query length: {len(request.query)}, {session_note}")

    try:
        result = await analysis_service.analyze(
            query=request.query,
            api_key=request.api_key,
            session_id=request.session_id,  # Can be None
            user_id=request.user_id
        )

        return AnalyzeResponse(**result)

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


# Session management endpoints (optional to use)
@app.post("/api/v1/sessions", response_model=SessionCreateResponse)
async def create_session(request: SessionCreateRequest):
    """
    Create new analysis session (optional)

    Use this to create a persistent session for multiple related requests.
    If you don't create a session, it will be auto-created per request.
    """
    logger.info(f"Session creation request for user: {request.user_id}")

    try:
        session_id = await analysis_service.create_session(request.user_id)

        return SessionCreateResponse(
            session_id=session_id,
            user_id=request.user_id,
            created_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Session creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session creation failed: {str(e)}"
        )


@app.get("/api/v1/sessions/{session_id}", response_model=SessionInfoResponse)
async def get_session_info(session_id: str):
    """Get session information with better error handling"""
    try:
        logger.info(f"Session info request: {session_id}")

        session_info = await analysis_service.get_session_info(session_id)

        if not session_info:
            logger.warning(f"Session not found: {session_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        logger.info(f"Session info returned for: {session_id}")
        return SessionInfoResponse(**session_info)

    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error retrieving session information: {str(e)}"
        )


# API status
@app.get("/api/v1/status")
async def api_status():
    """API status and endpoints"""
    return {
        "api_version": "v1",
        "status": "active",
        "session_mode": "optional",
        "endpoints": {
            "analyze": "POST /api/v1/analyze",
            "create_session": "POST /api/v1/sessions",
            "get_session": "GET /api/v1/sessions/{id}",
            "health": "GET /health"
        },
        "features": [
            "Optional session management",
            "Auto-session creation",
            "Context preservation",
            "Async processing",
            "Detailed responses"
        ]
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting {settings.app_name} v{settings.version}")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
