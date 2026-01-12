from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from thatsoundbot.settings import Settings
from thatsoundbot.core.langs.middleware import PipelineMiddleware


def create_bot(settings: Settings) -> Bot:
    """Creates and configures bot instance."""
    return Bot(
        token=settings.TOKEN.get_secret_value(),
        default=DefaultBotProperties()
    )


def create_dispatcher() -> Dispatcher:
    """Creates dispatcher instance with pipeline middleware."""
    dp = Dispatcher()

    dp.message.middleware(PipelineMiddleware())
    dp.callback_query.middleware(PipelineMiddleware())
    dp.inline_query.middleware(PipelineMiddleware())
    dp.chosen_inline_result.middleware(PipelineMiddleware())

    return dp
