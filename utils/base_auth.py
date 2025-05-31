from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

class BaseAuth(ABC):
    @abstractmethod
    async def create_access_token(self, data: dict, expires_delta: timedelta):
        pass

    @abstractmethod
    async def create_context_enriched_token(
        self,
        user_email: str,
        db: AsyncSession,
        expires_delta: timedelta,
        active_organization_id: Optional[int] = None,
        active_team_id: Optional[int] = None,
        custom_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        pass

    @abstractmethod
    async def create_refresh_token(self, data: dict, expires_delta: timedelta, db):
        pass

    @abstractmethod
    async def verify_token(self, token: str):
        pass