import sys
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.services import analysis_service
from .config import settings
from .models import (
    AnalyzeRequest, AnalyzeResponse,
    SessionCreateRequest, SessionCreateResponse,
    SessionInfoResponse, HealthResponse, ErrorResponse,
    SessionDeleteResponse
)

# Configure logging
logger.remove()
logger.add(sys.stdout, level=settings.log_level, format="{time} | {level} | {message}")

# Create FastAPI app with improved metadata
app = FastAPI(
    title="🤖 Staffing Analyzer API",
    version=settings.version,
    description="""
    🎯 Advanced AI-powered staffing request analysis

    This API provides intelligent analysis of staffing requests using Google's Generative AI.

    ✨ Key Features:
    * Smart Analysis - AI-powered text analysis for staffing requests
    * Flexible Sessions - Optional session management for context preservation
    * Auto Configuration - API key auto-loaded from environment
    * Real-time Processing - Async processing for better performance

    🚀 Quick Start:
    1. Set `GOOGLE_API_KEY` in your `.env` file
    2. Send POST request to `/api/v1/analyze` with just `{"query": "your text"}`
    3. Get intelligent analysis results instantly!

    📖 Documentation:
    * All endpoints support both session-based and sessionless requests
    * Session management is optional but recommended for multi-turn conversations
    * API key can be provided in request or loaded from environment
    """,
    debug=settings.debug,
    docs_url="/docs",
    redoc_url="/redoc",
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
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

# =============================================================================
# 🏠 GENERAL ENDPOINTS
# =============================================================================

@app.get(
    "/",
    tags=["🏠 General"],
    summary="API Information",
    description="Get basic information about the API, version, and available endpoints"
)
async def root():
    """
    ## API Information

    Returns basic information about the Staffing Analyzer API including:
    - API name and version
    - Current status
    - Links to documentation
    - Available endpoints overview
    """
    return {
        "name": "🤖 Staffing Analyzer API",
        "version": settings.version,
        "status": "🟢 running",
        "docs": "📖 /docs",
        "redoc": "📚 /redoc",
        "note": "💡 session_id and api_key are optional in /api/v1/analyze",
        "endpoints": {
            "analyze": "POST /api/v1/analyze",
            "sessions": "POST /api/v1/sessions",
            "health": "GET /health"
        },
        "quick_start": {
            "1": "Set GOOGLE_API_KEY in .env file",
            "2": "POST to /api/v1/analyze with {'query': 'your text'}",
            "3": "Get AI analysis results!"
        }
    }

@app.get(
    "/health",
    tags=["🏠 General"],
    response_model=HealthResponse,
    summary="System Health Check",
    description="Check the health status of the API and get system statistics"
)
async def health_check():
    """
    ## System Health Check

    Returns comprehensive health information including:
    - **Active sessions count** - Number of currently active analysis sessions
    - **Total requests** - Total number of analysis requests processed
    - **System status** - Overall health status of the service
    - **Timestamp** - Current server time

    Use this endpoint to monitor API availability and performance.
    """
    logger.info("Health check requested")
    health_info = analysis_service.health_check()

    return HealthResponse(
        active_sessions=health_info["active_sessions"],
        total_requests=health_info["total_requests"],
        status=health_info["status"]
    )

@app.get(
    "/api/v1/status",
    tags=["🏠 General"],
    summary="API Status & Features",
    description="Get detailed API status, version information, and feature list"
)
async def api_status():
    """
    ## API Status & Features

    Provides detailed information about:
    - API version and status
    - Session management mode
    - Available endpoints
    - Supported features
    """
    return {
        "api_version": "v1",
        "status": "🟢 active",
        "session_mode": "🔄 optional",
        "endpoints": {
            "analyze": "POST /api/v1/analyze",
            "create_session": "POST /api/v1/sessions",
            "get_session": "GET /api/v1/sessions/{id}",
            "delete_session": "DELETE /api/v1/sessions/{id}",
            "health": "GET /health"
        },
        "features": [
            "🤖 AI-powered analysis",
            "🔄 Optional session management",
            "⚡ Auto-session creation",
            "💾 Context preservation",
            "🚀 Async processing",
            "📊 Detailed responses",
            "🔧 Auto API key loading"
        ]
    }

# =============================================================================
# 🧠 ANALYSIS ENDPOINTS
# =============================================================================

# TODO add 429 error
@app.post(
    "/api/v1/analyze",
    tags=["🧠 Analysis"],
    response_model=AnalyzeResponse,
    summary="🎯 Analyze Staffing Request",
    description="Main endpoint for AI-powered analysis of staffing requests and job descriptions"
)
async def analyze(request: AnalyzeRequest):
    """
    ## 🎯 Analyze Staffing Request

    **Main endpoint for intelligent staffing request analysis using Google's Generative AI.**

    ### 📝 Input Parameters:
    - **query** *(required)*: The text you want to analyze (job description, staffing request, etc.)
    - **api_key** *(optional)*: Google API key (auto-loaded from GOOGLE_API_KEY env var if not provided)
    - **session_id** *(optional)*: Session ID for context preservation (auto-created if not provided)
    - **user_id** *(optional)*: User identifier (defaults to "user")

    ### 🎯 Use Cases:
    - **Job Description Analysis**: Analyze job requirements and responsibilities
    - **Skills Extraction**: Extract required skills and qualifications
    - **Candidate Matching**: Compare candidates against job requirements
    - **Requirements Clarification**: Get suggestions for improving job postings

    ### 💡 Pro Tips:
    - **No session_id?** → System auto-creates temporary session
    - **No api_key?** → Automatically loaded from `.env` file
    - **Need context?** → Use same session_id for related requests
    - **Multi-turn conversation?** → Create persistent session first

    ### 📊 Response:
    - **result**: AI analysis results
    - **session_id**: Session ID used (for follow-up requests)
    - **status**: success/error/no_response
    - **session_auto_created**: Indicates if session was auto-created
    - **timestamp**, **query_length**, **events_count**: Metadata
    """
    session_note = f"session: {request.session_id or 'auto-create'}"
    logger.info(f"Analysis request - query length: {len(request.query)}, {session_note}")

    try:
        result = await analysis_service.analyze(
            query=request.query,
            api_key=request.api_key,
            session_id=request.session_id,
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

@app.post(
    "/api/v1/analyze_parametrized",
    tags=["🧠 Analysis"],
    response_model=AnalyzeResponse,
    summary="🎯 Parametrized Analyze (with auto domain detect)",
    description="Анализ запроса с автодетектом домена (QA, DevOps и т.д.) и автоматическим выбором пайплайна"
)
async def analyze_parametrized(request: AnalyzeRequest):
    session_note = f"session: {request.session_id or 'auto-create'}"
    logger.info(f"Analysis request - query length: {len(request.query)}, {session_note}")

    try:
        print("Calling analysis_service.analyze_parametrized...")
        result = await analysis_service.analyze_parametrized(
            query=request.query,
            api_key=request.api_key,
            session_id=request.session_id,
            user_id=request.user_id,
            business_domain=request.business_domain
        )
        print("AnalyzeParametrized result received successfully")
        print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        return AnalyzeResponse(**result)
    except Exception as e:
        print(f"ERROR in analyze_parametrized endpoint: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise e

# =============================================================================
# 🔄 SESSION MANAGEMENT
# =============================================================================

@app.post(
    "/api/v1/sessions",
    tags=["🔄 Session Management"],
    response_model=SessionCreateResponse,
    summary="➕ Create New Session",
    description="Create a persistent session for multi-turn conversations and context preservation"
)
async def create_session(request: SessionCreateRequest):
    """
    ## ➕ Create New Session

    **Create a persistent session for maintaining context across multiple analysis requests.**

    ### 🎯 When to Use:
    - **Multi-turn conversations**: When you need to ask follow-up questions
    - **Context preservation**: When analysis should build on previous results
    - **User isolation**: When managing multiple users or workflows
    - **Performance optimization**: Reuse session instead of auto-creating each time

    ### 💡 Benefits:
    - **Context retention**: AI remembers previous interactions
    - **Better analysis**: Follow-up questions get contextual answers
    - **User experience**: Conversations feel natural and connected
    - **Performance**: Faster than creating new session each time

    ### 🔄 Usage Flow:
    1. **Create session** → Get session_id
    2. **Use session** → Include session_id in analysis requests
    3. **Continue conversation** → Keep using same session_id
    4. **Clean up** → Delete session when done (optional)

    ### 📝 Example:
    ```json
    POST /api/v1/sessions
    {"user_id": "john_doe"}

    Response: {"session_id": "sess_abc123", ...}

    POST /api/v1/analyze
    {"query": "Analyze this job description", "session_id": "sess_abc123"}

    POST /api/v1/analyze
    {"query": "What skills are most important?", "session_id": "sess_abc123"}
    ```
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

@app.get(
    "/api/v1/sessions/{session_id}",
    tags=["🔄 Session Management"],
    response_model=SessionInfoResponse,
    summary="📋 Get Session Info",
    description="Retrieve information about a specific session including usage statistics"
)
async def get_session_info(session_id: str):
    """
    ## 📋 Get Session Information

    **Retrieve detailed information about a specific session.**

    ### 📊 Returns:
    - **session_id**: The session identifier
    - **user_id**: User who owns the session
    - **created_at**: When the session was created
    - **requests_count**: Number of analysis requests made in this session

    ### 🎯 Use Cases:
    - **Usage tracking**: Monitor how much a session has been used
    - **Session validation**: Check if session exists before using
    - **Analytics**: Gather usage statistics
    - **Debugging**: Troubleshoot session-related issues

    ### ⚠️ Notes:
    - Returns **404** if session doesn't exist
    - Auto-created sessions are cleaned up periodically
    - Session data is kept in memory (lost on server restart)
    """
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
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error retrieving session information: {str(e)}"
        )

@app.delete(
    "/api/v1/sessions/{session_id}",
    tags=["🔄 Session Management"],
    response_model=SessionDeleteResponse,
    summary="🗑️ Delete Session",
    description="Delete a session and free up resources"
)
async def delete_session(session_id: str):
    """
    ## 🗑️ Delete Session

    **Permanently delete a session and free up associated resources.**

    ### 🎯 When to Use:
    - **Cleanup**: When conversation is finished
    - **Privacy**: Remove user data from memory
    - **Resource management**: Free up memory
    - **Security**: Clear sensitive session data

    ### ⚠️ Important:
    - **Permanent action**: Cannot be undone
    - **Context lost**: All conversation history is removed
    - **Future requests**: Will need new session or auto-creation
    - **Already deleted**: Returns success even if session doesn't exist

    ### 💡 Best Practices:
    - Delete sessions when user logs out
    - Clean up temporary sessions after use
    - Don't delete if you plan to continue conversation
    - Auto-created sessions clean themselves up

    ### 📝 Example:
    ```json
    DELETE /api/v1/sessions/sess_abc123

    Response: {
        "success": true,
        "session_id": "sess_abc123",
        "message": "Session deleted successfully"
    }
    ```
    """
    try:
        logger.info(f"Session deletion request: {session_id}")

        success = await analysis_service.delete_session(session_id)

        if success:
            logger.info(f"Session deleted successfully: {session_id}")
            return SessionDeleteResponse(
                success=True,
                session_id=session_id,
                message="Session deleted successfully"
            )
        else:
            logger.warning(f"Session not found for deletion: {session_id}")
            # Return success even if session doesn't exist (idempotent)
            return SessionDeleteResponse(
                success=True,
                session_id=session_id,
                message="Session not found (may have been already deleted)"
            )

    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting {settings.app_name} v{settings.version}")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
