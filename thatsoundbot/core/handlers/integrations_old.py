from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from thatsoundbot.core.handlers.messages.texts import TEXTS
from thatsoundbot.core.keyboards.integrations import update_integrations_keyboard
from thatsoundbot.repositories.users import mention_user
from thatsoundbot.settings import get_integrations, get_settings
from thatsoundbot.utils.hashing import hash_telegram_id

router = Router(name="integrations")


@router.callback_query(F.data.startswith("integration:"))
async def integration_callback_handler(callback: CallbackQuery) -> None:
    """Handle integration button callbacks."""
    if not callback.data:
        await callback.answer()
        return

    parts = callback.data.split(":")
    if len(parts) != 3 or parts[0] != "integration" or parts[2] != "connected":
        await callback.answer()
        return

    await callback.answer(TEXTS["integrations"]["connected_alert"], show_alert=True)
