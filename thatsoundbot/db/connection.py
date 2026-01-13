from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from thatsoundbot.db.redis import RedisClient

redis_client: ContextVar["RedisClient | None"] = ContextVar("redis_client", default=None)
