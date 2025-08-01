"""Business logic services"""

from typing import Optional, Dict, Any
from loguru import logger
from .backend_logic import analyzer


class AnalysisService:
    """Service layer for analysis operations"""

    def __init__(self):
        logger.info("AnalysisService initialized")

    @staticmethod
    async def analyze(
            query: str,
            api_key: str,
            session_id: Optional[str] = None,
            user_id: str = "user"
    ) -> Dict[str, Any]:
        """Analyze query using backend"""
        return await analyzer.analyze(query, api_key, session_id, user_id)

    @staticmethod
    async def create_session(user_id: str = "user") -> str:
        """Create new session"""
        return await analyzer.create_session(user_id)

    @staticmethod
    async def get_session_info(session_id: str) -> Optional[Dict]:
        """Get session info"""
        return await analyzer.get_session_info(session_id)

    @staticmethod
    def health_check() -> Dict[str, Any]:
        """Health check"""
        return analyzer.get_stats()


# Global service instance
analysis_service = AnalysisService()
