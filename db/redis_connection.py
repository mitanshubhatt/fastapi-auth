import redis.asyncio as redis
from typing import Optional
from fastapi import HTTPException
from datetime import timedelta
from utils.custom_logger import logger

class RedisClient:

    def __init__(self, redis_url: str = "redis://redis:6379/1"):
        self.redis_url = redis_url
        self.redis = None

    async def connect(self):
        """Connect to Redis."""
        if not self.redis:
            self.redis = redis.from_url(self.redis_url, decode_responses=True)
            logger.info(f"Connected to Redis at {self.redis_url}")

    async def close(self):
        """Close the Redis connection."""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")

    async def set(self, key: str, value: str, expire: Optional[timedelta] = None):
        """Set a value in Redis with optional expiration."""
        try:
            if expire:
                await self.redis.setex(key, expire, value)
            else:
                await self.redis.set(key, value)
            logger.info(f"Set key '{key}' in Redis with value: {value}")
        except Exception as e:
            logger.error(f"Error setting key '{key}' in Redis: {e}")
            raise HTTPException(status_code=500, detail="Error interacting with Redis")

    async def get(self, key: str) -> Optional[str]:
        """Get a value from Redis by key."""
        try:
            value = await self.redis.get(key)
            if value is None:
                logger.warning(f"Key '{key}' not found in Redis.")
            return value
        except Exception as e:
            logger.error(f"Error getting key '{key}' from Redis: {e}")
            raise HTTPException(status_code=500, detail="Error interacting with Redis")

    async def delete(self, key: str):
        """Delete a key from Redis."""
        try:
            await self.redis.delete(key)
            logger.info(f"Deleted key '{key}' from Redis.")
        except Exception as e:
            logger.error(f"Error deleting key '{key}' from Redis: {e}")
            raise HTTPException(status_code=500, detail="Error interacting with Redis")

    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis."""
        try:
            exists = await self.redis.exists(key)
            return exists == 1
        except Exception as e:
            logger.error(f"Error checking existence of key '{key}' in Redis: {e}")
            raise HTTPException(status_code=500, detail="Error interacting with Redis")
