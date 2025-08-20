from typing import Optional, Dict, Any
from loguru import logger
from .backend_logic import backendAnalyzer


class AnalysisService:
    """Service layer for analysis operations"""

    def __init__(self):
        logger.info("AnalysisService initialized")

    async def analyze(
            self,
            query: str,
            api_key: str,
            session_id: Optional[str] = None,
            user_id: str = "user"
    ) -> Dict[str, Any]:
        """Analyze query using backend"""
        return await backendAnalyzer.analyze(query, api_key, session_id, user_id)

    async def analyze_parametrized(
            self,
            query: str,
            api_key: str,
            session_id: Optional[str] = None,
            user_id: str = "user",
            business_domain: Optional[str] = None
    ) -> Dict[str, Any]:
        return await backendAnalyzer.analyze_parametrized(
            query, api_key, session_id, user_id, business_domain
        )

    async def create_session(self, user_id: str = "user") -> str:
        """Create new session"""
        return await backendAnalyzer.create_session(user_id)

    async def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session info"""
        return await backendAnalyzer.get_session_info(session_id)

    def health_check(self) -> Dict[str, Any]:
        """Health check"""
        return backendAnalyzer.get_stats()

    async def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        return await backendAnalyzer.delete_session(session_id)


# Global service instance
analysis_service = AnalysisService()
