from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from thatsoundbot.db.redis import RedisClient


class RedisMiddleware(BaseMiddleware):
    """
    Middleware for injecting Redis client into handlers.

    Creates a new Redis connection for each handler call and automatically
    closes it after the handler completes (even if an exception occurs).
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """
        Inject Redis client into handler data.

        The connection is automatically closed when the handler finishes,
        thanks to the async context manager protocol.
        """
        redis_client = RedisClient()
        async with redis_client:
            data["redis"] = redis_client
            return await handler(event, data)
