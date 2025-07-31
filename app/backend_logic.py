import os
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger

# Google ADK imports
from google.genai import types
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from staffing_request_pipeline.agent import root_agent


class StaffingAnalyzer:
    """
    Staffing analyzer with optional session support
    """

    def __init__(self):
        self.session_service = InMemorySessionService()
        self.artifact_service = InMemoryArtifactService()
        self.active_sessions: Dict[str, Any] = {}
        logger.info("StaffingAnalyzer initialized")

    async def create_session(self, user_id: str = "user") -> str:
        """Create new analysis session"""
        session = await self.session_service.create_session(
            app_name="StaffingAnalyzer",
            user_id=user_id
        )

        session_id = session.id # Проблемы с сессией айди тутачцы были
        self.active_sessions[session_id] = {
            'session': session,
            'created_at': datetime.now(),
            'user_id': user_id,
            'requests_count': 0
        }

        logger.info(f"Created session: {session_id}")
        return session_id

    async def analyze(
        self,
        query: str,
        api_key: str,
        session_id: Optional[str] = None,
        user_id: str = "user"
    ) -> Dict[str, Any]:
        """Main analysis method - session_id is optional"""

        # Validation
        if not query.strip():
            raise ValueError("Query cannot be empty")
        if not api_key.strip():
            raise ValueError("API key cannot be empty")

        # Set Google API key
        os.environ['GOOGLE_API_KEY'] = api_key

        # Handle session - create if not provided or invalid
        session_auto_created = False
        if session_id and session_id in self.active_sessions:
            session = self.active_sessions[session_id]['session']
            self.active_sessions[session_id]['requests_count'] += 1
            logger.info(f"Using existing session: {session_id}")
        else:
            # Auto-create session for this request
            session_id = await self.create_session(user_id)
            session = self.active_sessions[session_id]['session']
            session_auto_created = True
            logger.info(f"Auto-created session: {session_id}")

        # Setup runner
        runner = Runner(
            app_name="StaffingAnalyzer",
            agent=root_agent,
            artifact_service=self.artifact_service,
            session_service=self.session_service,
        )

        # Create content
        content = types.Content(
            role="user",
            parts=[types.Part(text=query)]
        )

        logger.info(f"Starting analysis for session {session_id}")

        try:
            # Run analysis
            events_result = runner.run(
                user_id=user_id,
                session_id=session.id,
                new_message=content
            )

            # Handle async or sync events
            if hasattr(events_result, '__aiter__'):
                # Async generator
                events = []
                async for event in events_result:
                    events.append(event)
            else:
                # Regular iterable
                events = list(events_result)

            # Process results
            if events:
                last_event = events[-1]
                result = "".join(
                    [part.text for part in last_event.content.parts if part.text]
                )

                return {
                    "result": result or "Analysis completed but no text response generated.",
                    "session_id": session_id,
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                    "query_length": len(query),
                    "events_count": len(events),
                    "session_auto_created": session_auto_created
                }
            else:
                return {
                    "result": "No response generated from the analysis.",
                    "session_id": session_id,
                    "status": "no_response",
                    "timestamp": datetime.now().isoformat(),
                    "session_auto_created": session_auto_created
                }

        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return {
                "result": f"Analysis failed: {str(e)}",
                "session_id": session_id,
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "session_auto_created": session_auto_created
            }

    async def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session information"""
        if session_id in self.active_sessions:
            info = self.active_sessions[session_id].copy()
            info['created_at'] = info['created_at'].isoformat()
            del info['session']  # Don't expose session object
            return info
        return None

    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        total_requests = sum(
            s['requests_count'] for s in self.active_sessions.values()
        )

        return {
            "active_sessions": len(self.active_sessions),
            "total_requests": total_requests,
            "status": "healthy"
        }


# Global instance
analyzer = StaffingAnalyzer()
