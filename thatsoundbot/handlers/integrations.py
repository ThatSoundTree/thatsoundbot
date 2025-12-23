from aiogram import F, Router
from aiogram.types import CallbackQuery

from thatsoundbot.handlers.messages.start import TEXTS

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
