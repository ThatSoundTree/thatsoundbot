from typing import Awaitable, Optional
import json
from uuid import UUID

import redis.asyncio as redis
from loguru import logger

from thatsoundbot.core.models.tsapi import TrackView
from thatsoundbot.settings import get_settings


class RedisClient:
    _client: Optional[redis.Redis] = None

    @classmethod
    async def startup(cls) -> None:
        if cls._client is not None:
            return

        settings = get_settings()

        cls._client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
        )

        try:
            await cls._client.ping()
        except Exception:
            logger.exception("Failed to connect to Redis")
            raise

        logger.info("Redis client initialized")

    @classmethod
    async def shutdown(cls) -> None:
        if cls._client is None:
            return

        await cls._client.aclose()
        cls._client = None

        logger.info("Redis client closed")

    @classmethod
    def client(cls) -> redis.Redis:
        if cls._client is None:
            raise RuntimeError("Redis client is not initialized")
        return cls._client


class RedisService:

    def __init__(self, redis_client: redis.Redis) -> None:
        self._redis = redis_client

    async def has_spotify_integration(self, hgramid: str) -> bool:
        """Check if user has Spotify integration (instance method)."""
        return bool(await self._redis.exists(f"spotify:tokens:{hgramid}"))

    async def has_yandex_music_integration(self, hgramid: str) -> bool:
        """Check if user has Yandex Music integration (instance method)."""
        return bool(await self._redis.exists(f"yandex:token:{hgramid}"))

    async def save_result_query(self, result_id: str, track: TrackView, ttl: int) -> None:
        hash_key = "results"
        track_dict = track.model_dump(mode='json')
        track_dict['provider'] = track.provider
        track_json = json.dumps(track_dict)

        result = self._redis.hset(hash_key, result_id, track_json)
        if isinstance(result, Awaitable):
            await result

        expire_result = self._redis.expire(hash_key, ttl)
        if isinstance(expire_result, Awaitable):
            await expire_result

    async def get_result_query(self, result_id: str) -> TrackView | None:
        """Get track query result (instance method)."""
        result = self._redis.hget("results", result_id)
        result_value: str | None = await result if isinstance(result, Awaitable) else result
        if result_value is not None:
            track_dict = json.loads(result_value)
            return TrackView.model_validate(track_dict)
        return None

    async def get_track_path(self, scrobble_id: UUID) -> str | None:
        result = await self._redis.get(name=f"cache:scrobble:{scrobble_id.hex}")
        return result if result is not None else None

    async def get_track_thumbnail_path(self, scrobble_id: UUID) -> str | None:
        result = await self._redis.get(name=f"cache:scrobble:{scrobble_id.hex}:thumbnail")
        return result if result is not None else None
