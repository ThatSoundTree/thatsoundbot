from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from thatsoundbot.settings import Settings


def create_bot(settings: Settings) -> Bot:
    """Creates and configures bot instance."""
    return Bot(
        token=settings.TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    """Creates dispatcher instance."""
    return Dispatcher()
