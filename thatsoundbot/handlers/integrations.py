from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from thatsoundbot.handlers.messages.texts import TEXTS
from thatsoundbot.keyboards.integrations import update_integrations_keyboard
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


@router.callback_query(F.data == "refresh_status")
async def refresh_status_handler(callback: CallbackQuery) -> None:
    """Handle refresh status button callback."""
    if not callback.from_user or not callback.message:
        await callback.answer()
        return

    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    old_keyboard = callback.message.reply_markup
    telegram_id = callback.from_user.id
    htelegram_id = hash_telegram_id(telegram_id)

    if old_keyboard and old_keyboard.inline_keyboard:
        loading_rows = []
        for row in old_keyboard.inline_keyboard:
            loading_row = []
            for button in row:
                if button.callback_data == "refresh_status":
                    loading_row.append(
                        InlineKeyboardButton(
                            text=TEXTS["integrations"]["refresh_button_loading"],
                            callback_data="refresh_status",
                        )
                    )
                else:
                    loading_row.append(button)
            loading_rows.append(loading_row)
        loading_keyboard = InlineKeyboardMarkup(inline_keyboard=loading_rows)

        await callback.message.edit_reply_markup(reply_markup=loading_keyboard)

    old_integrations_status = {}
    if old_keyboard and old_keyboard.inline_keyboard:
        settings = get_settings()
        for row in old_keyboard.inline_keyboard:
            for button in row:
                if button.callback_data and button.callback_data.startswith("integration:"):
                    parts = button.callback_data.split(":")
                    if len(parts) == 3:
                        integration_name = parts[1]
                        is_connected = parts[2] == "connected"
                        old_integrations_status[integration_name] = is_connected
                elif button.url:
                    for integration_config in get_integrations():
                        expected_url = integration_config["connect_url_template"].format(
                            api_public_url=settings.API_PUBLIC_URL, htelegram_id=htelegram_id
                        )
                        if button.url == expected_url:
                            old_integrations_status[integration_config["name"]] = False
                            break

    user = await mention_user(htelegram_id)

    new_integrations_data = user.integrations.model_dump()
    changed_integrations = []

    for integration_name, is_enabled in new_integrations_data.items():
        old_status = old_integrations_status.get(integration_name, None)
        if old_status is not None and old_status != is_enabled:
            changed_integrations.append(integration_name)

    keyboard_to_update = callback.message.reply_markup or old_keyboard
    updated_keyboard = update_integrations_keyboard(
        keyboard_to_update, user, htelegram_id, refresh_button_loading=False
    )
    await callback.message.edit_reply_markup(reply_markup=updated_keyboard)

    if changed_integrations:
        changed_names = ", ".join([name.capitalize() for name in changed_integrations])
        await callback.answer(
            f"{TEXTS['integrations']['status_updated']}: {changed_names}",
            show_alert=True,
        )
    else:
        await callback.answer()
