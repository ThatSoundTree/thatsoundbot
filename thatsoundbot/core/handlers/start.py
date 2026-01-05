from aiogram.enums import ParseMode
from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from thatsoundbot.core.handlers.messages import format_start_message
from thatsoundbot.models.pipelines_view import PipelineView
from thatsoundbot.repositories.users import mention_user
from thatsoundbot.services.integrations import get_user_integrations
from thatsoundbot.utils.hashing import hash_telegram_id

router = Router(name="start")


@router.message(Command("start"))
async def start_handler(message: Message, pipeline: PipelineView) -> None:
    """Handles the /start command for greeting."""
    hgramid = hash_telegram_id(message.from_user.id)
    integrations = await get_user_integrations(hgramid=hgramid)

    await message.answer(pipeline.welcome_message, parse_mode=ParseMode.MARKDOWN)
    #
    # is_new = user.message is not None
    # logger.info(f"User mentioned: htelegram_id={htelegram_id[:8]}, new={is_new}")
    #
    # text, keyboard = format_start_message(user, htelegram_id)
    # await message.answer(text, reply_markup=keyboard)
