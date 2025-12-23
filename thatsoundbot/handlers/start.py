from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from thatsoundbot.backend.api import mention_user
from thatsoundbot.handlers.messages import format_start_message
from thatsoundbot.utils.hashing import hash_telegram_id

router = Router(name="start")


@router.message(Command("start"))
async def start_handler(message: Message) -> None:
    """Handles the /start command and responds with a greeting."""
    if not message.from_user:
        return

    telegram_id = message.from_user.id
    htelegram_id = hash_telegram_id(telegram_id)
    user = await mention_user(htelegram_id)

    text, keyboard = format_start_message(user, htelegram_id)
    await message.answer(text, reply_markup=keyboard)
