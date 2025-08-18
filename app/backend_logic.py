import os
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger

# Google ADK imports
from google.genai import types
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from staffing_chainable_agents_request_pipeline.agent import create_parametrized_pipeline
from staffing_chainable_agents_request_pipeline.utils import validate_business_domain
from staffing_request_pipeline.agent import root_agent


class StaffingAnalyzer:
    """
    Staffing analyzer with auto-cleanup of temporary sessions
    """

    def __init__(self):
        self.session_service = InMemorySessionService()
        self.artifact_service = InMemoryArtifactService()
        self.active_sessions: Dict[str, Any] = {}
        self.total_requests_counter = 0
        logger.info("StaffingAnalyzer initialized")

    async def create_session(self, user_id: str = "user", auto_created: bool = False) -> str:
        """Create new analysis session"""
        session = await self.session_service.create_session(
            app_name="StaffingAnalyzer",
            user_id=user_id
        )

        session_id = session.id
        self.active_sessions[session_id] = {
            'session': session,
            'created_at': datetime.now(),
            'user_id': user_id,
            'requests_count': 0,
            'auto_created': auto_created  # ← ПОМЕЧАЕМ АВТОСОЗДАННЫЕ
        }

        logger.info(f"Created session: {session_id} (auto_created: {auto_created})")
        return session_id

    async def analyze(
            self,
            query: str,
            api_key: str,
            session_id: Optional[str] = None,
            user_id: str = "user"
    ) -> Dict[str, Any]:
        """Main analysis method with auto-cleanup"""

        # Увеличиваем глобальный счетчик
        self.total_requests_counter += 1

        # Validation
        if not query.strip():
            raise ValueError("Query cannot be empty")
        if not api_key.strip():
            raise ValueError("API key cannot be empty")

        # Set Google API key
        os.environ['GOOGLE_API_KEY'] = api_key

        # Handle session
        session_auto_created = False
        if session_id and session_id in self.active_sessions:
            session = self.active_sessions[session_id]['session']
            self.active_sessions[session_id]['requests_count'] += 1
            logger.info(f"Using existing session: {session_id}")
        else:
            # Auto-create session with auto_created flag
            session_id = await self.create_session(user_id, auto_created=True)
            session = self.active_sessions[session_id]['session']
            self.active_sessions[session_id]['requests_count'] = 1
            session_auto_created = True
            logger.info(f"Auto-created temporary session: {session_id}")

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

        logger.info(f"Starting analysis for session {session_id} (total requests: {self.total_requests_counter})")

        try:
            # Run analysis
            events_result = runner.run(
                user_id=user_id,
                session_id=session.id,
                new_message=content
            )

            # Handle async or sync events
            if hasattr(events_result, '__aiter__'):
                events = []
                async for event in events_result:
                    events.append(event)
            else:
                events = list(events_result)

            # Process results
            result_data = None
            if events:
                last_event = events[-1]
                result = "".join(
                    [part.text for part in last_event.content.parts if part.text]
                )

                result_data = {
                    "result": result or "Analysis completed but no text response generated.",
                    "session_id": session_id,
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                    "query_length": len(query),
                    "events_count": len(events),
                    "session_auto_created": session_auto_created
                }
            else:
                result_data = {
                    "result": "No response generated from the analysis.",
                    "session_id": session_id,
                    "status": "no_response",
                    "timestamp": datetime.now().isoformat(),
                    "session_auto_created": session_auto_created
                }

            # 🗑️ AUTO-CLEANUP: Delete auto-created session after successful analysis
            if session_auto_created:
                await self._cleanup_auto_session(session_id)

            return result_data

        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")

            # 🗑️ AUTO-CLEANUP: Delete auto-created session even on error
            if session_auto_created:
                await self._cleanup_auto_session(session_id)

            return {
                "result": f"Analysis failed: {str(e)}",
                "session_id": session_id,
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "session_auto_created": session_auto_created
            }

    async def analyze_parametrized(
            self,
            query: str,
            api_key: str,
            session_id: Optional[str] = None,
            user_id: str = "user",
            business_domain: Optional[str] = None  # <-- ДОБАВЛЯЕМ
    ) -> Dict[str, Any]:
        """
        Анализ c автоопределением или ручным указанием домена.
        """
        self.total_requests_counter += 1
        if not query.strip():
            raise ValueError("Query cannot be empty")
        if not api_key.strip():
            raise ValueError("API key cannot be empty")
        os.environ['GOOGLE_API_KEY'] = api_key

        session_auto_created = False
        if session_id and session_id in self.active_sessions:
            session = self.active_sessions[session_id]['session']
            self.active_sessions[session_id]['requests_count'] += 1
        else:
            session_id = await self.create_session(user_id, auto_created=True)
            session = self.active_sessions[session_id]['session']
            self.active_sessions[session_id]['requests_count'] = 1
            session_auto_created = True

        # 1. Выбираем домен: либо от пользователя, либо авто
        if business_domain and business_domain.strip():
            chosen_domain = validate_business_domain(business_domain)
        else:
            chosen_domain = "AQA"

        # 2. Создаем пайплайн
        root_agent_param = create_parametrized_pipeline(chosen_domain)  # ← здесь домен передаем напрямую!

        runner = Runner(
            app_name="StaffingAnalyzer",
            agent=root_agent_param,
            artifact_service=self.artifact_service,
            session_service=self.session_service,
        )

        content = types.Content(role="user", parts=[types.Part(text=query)])
        try:
            events_result = runner.run(
                user_id=user_id,
                session_id=session.id,
                new_message=content
            )
            if hasattr(events_result, '__aiter__'):
                events = []
                async for event in events_result:
                    events.append(event)
            else:
                events = list(events_result)

            result_data = None
            if events:
                last_event = events[-1]
                result = "".join([part.text for part in last_event.content.parts if part.text])
                result_data = {
                    "result": result or "Analysis completed but no text response generated.",
                    "session_id": session_id,
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                    "query_length": len(query),
                    "events_count": len(events),
                    "session_auto_created": session_auto_created
                }
            else:
                result_data = {
                    "result": "No response generated from the analysis.",
                    "session_id": session_id,
                    "status": "no_response",
                    "timestamp": datetime.now().isoformat(),
                    "session_auto_created": session_auto_created
                }

            if session_auto_created:
                await self._cleanup_auto_session(session_id)
            return result_data

        except Exception as e:
            if session_auto_created:
                await self._cleanup_auto_session(session_id)
            return {
                "result": f"Analysis failed: {str(e)}",
                "session_id": session_id,
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "session_auto_created": session_auto_created
            }

    async def _cleanup_auto_session(self, session_id: str):
        """Internal method to clean up auto-created sessions"""
        try:
            if session_id in self.active_sessions:
                session_data = self.active_sessions[session_id]
                if session_data.get('auto_created', False):
                    del self.active_sessions[session_id]
                    logger.info(f"Auto-cleaned temporary session: {session_id}")
                else:
                    logger.debug(f"Skipped cleanup for persistent session: {session_id}")
        except Exception as e:
            logger.error(f"Error during auto-cleanup of session {session_id}: {str(e)}")

    async def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session information"""
        try:
            if session_id in self.active_sessions:
                session_data = self.active_sessions[session_id]

                info = {
                    'session_id': session_id,
                    'user_id': session_data['user_id'],
                    'created_at': session_data['created_at'].isoformat(),
                    'requests_count': session_data['requests_count'],
                    'auto_created': session_data.get('auto_created', False)  # ← ДОБАВЛЯЕМ ФЛАГ
                }

                logger.info(f"Session info retrieved: {session_id}")
                return info
            else:
                logger.warning(f"Session not found: {session_id}")
                return None

        except Exception as e:
            logger.error(f"Error getting session info for {session_id}: {str(e)}")
            return None

    async def delete_session(self, session_id: str) -> bool:
        """Delete a specific session"""
        try:
            if session_id in self.active_sessions:
                session_data = self.active_sessions[session_id]
                was_auto_created = session_data.get('auto_created', False)
                del self.active_sessions[session_id]
                logger.info(f"Session deleted: {session_id} (was_auto_created: {was_auto_created})")
                return True
            else:
                logger.warning(f"Session not found for deletion: {session_id}")
                return False
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {str(e)}")
            raise e

    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        session_requests = sum(
            s['requests_count'] for s in self.active_sessions.values()
        )

        auto_created_count = sum(
            1 for s in self.active_sessions.values() if s.get('auto_created', False)
        )

        persistent_count = len(self.active_sessions) - auto_created_count

        return {
            "active_sessions": len(self.active_sessions),
            "persistent_sessions": persistent_count,
            "auto_created_sessions": auto_created_count,
            "total_requests": self.total_requests_counter,
            "session_requests": session_requests,
            "status": "healthy"
        }


# Global instance
backendAnalyzer = StaffingAnalyzer()
