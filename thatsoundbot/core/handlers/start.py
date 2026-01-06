from aiogram.enums import ParseMode
from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from thatsoundbot.core.handlers.messages import format_start_message
from thatsoundbot.core.keyboards.integrations import prepare_integrate_keyboard
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

    keyboard = prepare_integrate_keyboard(hgramid=hgramid, integrations=integrations, pipeline=pipeline)
    await message.answer(pipeline.welcome_message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)
