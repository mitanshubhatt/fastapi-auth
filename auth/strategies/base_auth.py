from abc import ABC, abstractmethod
from datetime import timedelta

class BaseAuth(ABC):
    @abstractmethod
    async def create_access_token(self, data: dict, expires_delta: timedelta):
        pass

    @abstractmethod
    async def create_refresh_token(self, data: dict, expires_delta: timedelta, db):
        pass

    @abstractmethod
    async def verify_token(self, token: str):
        pass