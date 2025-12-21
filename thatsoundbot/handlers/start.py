from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from loguru import logger

from thatsoundbot.backend.api import mention_user
from thatsoundbot.utils.hashing import hash_telegram_id

router = Router(name="start")


@router.message(Command("start"))
async def start_handler(message: Message) -> None:
    """Handles the /start command and responds with a greeting."""
    user_name = message.from_user.full_name if message.from_user else "Пользователь"

    if message.from_user:
        telegram_id = message.from_user.id
        htelegram_id = hash_telegram_id(telegram_id)
        result = await mention_user(htelegram_id)
        logger.debug("User mention result for telegram_id={}: {}", telegram_id, result)

    greeting = f"Привет, {hbold(user_name)}!"
    await message.answer(greeting)
