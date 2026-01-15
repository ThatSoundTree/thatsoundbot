import asyncio

from aiogram.enums import ParseMode

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from thatsoundbot.core.keyboards.integrations import prepare_integrate_keyboard
from thatsoundbot.core.models.pipelines_view import PipelineView
from thatsoundbot.db.redis import RedisService
from thatsoundbot.services.integrations import get_user_integrations, create_remote_user

router = Router(name="integrations")


@router.message(Command("start"))
async def start_handler(message: Message, redis: RedisService, hgramid: str, pipeline: PipelineView) -> None:
    """Handles the start menu."""

    integrations, _ = await asyncio.gather(
        get_user_integrations(redis=redis, hgramid=hgramid),
        create_remote_user(hgramid=hgramid)
    )

    old_keyboard = message.reply_to_message.reply_markup if message.reply_to_message else None
    keyboard = prepare_integrate_keyboard(hgramid=hgramid, integrations=integrations, pipeline=pipeline)

    if old_keyboard and old_keyboard.model_dump_json() == keyboard.model_dump_json():
        return

    await message.answer(pipeline.welcome_message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)


@router.callback_query(F.data == "integration:refresh")
async def refresh_status_handler(callback: CallbackQuery, redis: RedisService, hgramid: str, pipeline: PipelineView) -> None:
    """Handle refresh status button callback."""
    if not callback.message or not isinstance(callback.message, Message):
        await callback.answer()
        return

    integrations = await get_user_integrations(redis=redis, hgramid=hgramid)
    old_keyboard = callback.message.reply_markup
    keyboard = prepare_integrate_keyboard(hgramid=hgramid, integrations=integrations, pipeline=pipeline)

    if old_keyboard and old_keyboard.model_dump_json() == keyboard.model_dump_json():
        await callback.answer()
        return

    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "integration:connected")
async def integration_callback_handler(callback: CallbackQuery, pipeline: PipelineView) -> None:
    """Handle integration button callbacks."""
    await callback.answer(pipeline.integrations.already_connected, show_alert=True)
