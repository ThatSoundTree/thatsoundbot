from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from thatsoundbot.settings import Settings
from thatsoundbot.core.langs.middleware import PipelineMiddleware
from thatsoundbot.core.langs.redis_middleware import RedisMiddleware
from thatsoundbot.core.middlewares import create_error_router


def create_bot(settings: Settings) -> Bot:
    """Creates and configures bot instance."""
    return Bot(
        token=settings.TOKEN.get_secret_value(),
        default=DefaultBotProperties()
    )


def create_dispatcher() -> Dispatcher:
    """Creates dispatcher instance with pipeline and redis middleware."""
    dp = Dispatcher()

    # Register error handlers router first (to catch all errors)
    error_router = create_error_router()
    dp.include_router(error_router)

    # Register Redis middleware
    dp.message.middleware(RedisMiddleware())
    dp.callback_query.middleware(RedisMiddleware())
    dp.inline_query.middleware(RedisMiddleware())
    dp.chosen_inline_result.middleware(RedisMiddleware())

    # Register Pipeline middleware
    dp.message.middleware(PipelineMiddleware())
    dp.callback_query.middleware(PipelineMiddleware())
    dp.inline_query.middleware(PipelineMiddleware())
    dp.chosen_inline_result.middleware(PipelineMiddleware())

    return dp
