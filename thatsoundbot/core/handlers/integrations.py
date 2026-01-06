from aiogram.enums import ParseMode

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from thatsoundbot.core.keyboards.integrations import prepare_integrate_keyboard
from thatsoundbot.models.pipelines_view import PipelineView
from thatsoundbot.services.integrations import get_user_integrations


router = Router(name="integrations")


@router.message(Command("start"))
async def start_handler(message: Message, hgramid: str, pipeline: PipelineView) -> None:
    """Handles the start menu."""
    integrations = await get_user_integrations(hgramid=hgramid)

    keyboard = prepare_integrate_keyboard(hgramid=hgramid, integrations=integrations, pipeline=pipeline)
    await message.answer(pipeline.welcome_message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)


@router.callback_query(F.data == "integration:refresh")
async def refresh_status_handler(callback: CallbackQuery, hgramid: str, pipeline: PipelineView) -> None:
    """Handle refresh status button callback."""
    integrations = await get_user_integrations(hgramid=hgramid)
    old_keyboard = callback.message.reply_markup
    keyboard = prepare_integrate_keyboard(hgramid=hgramid, integrations=integrations, pipeline=pipeline)

    if old_keyboard.model_dump_json() == keyboard.model_dump_json():
        await callback.answer()
        return

    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "integration:connected")
async def integration_callback_handler(callback: CallbackQuery, hgramid: str, pipeline: PipelineView) -> None:
    """Handle integration button callbacks."""
    await callback.answer(pipeline.integrations.already_connected, show_alert=True)
