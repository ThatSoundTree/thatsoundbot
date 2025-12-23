from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from thatsoundbot.backend.api import mention_user
from thatsoundbot.handlers.messages.texts import TEXTS
from thatsoundbot.keyboards.integrations import update_integrations_keyboard
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

    # Type check: ensure message is Message, not InaccessibleMessage
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    # Get current keyboard and save it for error recovery
    old_keyboard = callback.message.reply_markup
    telegram_id = callback.from_user.id
    htelegram_id = hash_telegram_id(telegram_id)

    # Step 1: Show loading animation - change refresh button to "обновление 👀"
    if old_keyboard and old_keyboard.inline_keyboard:
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

        loading_rows = []
        for row in old_keyboard.inline_keyboard:
            loading_row = []
            for button in row:
                if button.callback_data == "refresh_status":
                    # Replace with loading button
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

        try:
            await callback.message.edit_reply_markup(reply_markup=loading_keyboard)
        except Exception:
            # If edit fails, continue anyway
            pass

    try:
        # Get old integration statuses from original keyboard (before loading state)
        old_integrations_status = {}
        if old_keyboard and old_keyboard.inline_keyboard:
            from thatsoundbot.settings import get_settings, get_integrations

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
                        # Check if it's an integration URL button
                        for integration_config in get_integrations():
                            expected_url = integration_config["connect_url_template"].format(
                                api_url=settings.API_URL, htelegram_id=htelegram_id
                            )
                            if button.url == expected_url:
                                old_integrations_status[integration_config["name"]] = False
                                break

        # Fetch updated user data from backend
        user = await mention_user(htelegram_id)

        # Compare old and new statuses to detect changes
        new_integrations_data = user.integrations.model_dump()
        changed_integrations = []

        for integration_name, is_enabled in new_integrations_data.items():
            old_status = old_integrations_status.get(integration_name, None)
            if old_status is not None and old_status != is_enabled:
                changed_integrations.append(integration_name)

        # Update keyboard - only changed buttons will be updated
        # Use current keyboard (might have loading state) or old keyboard
        keyboard_to_update = callback.message.reply_markup or old_keyboard
        updated_keyboard = update_integrations_keyboard(
            keyboard_to_update, user, htelegram_id, refresh_button_loading=False
        )
        await callback.message.edit_reply_markup(reply_markup=updated_keyboard)

        # Show notification if something changed
        if changed_integrations:
            changed_names = ", ".join([name.capitalize() for name in changed_integrations])
            await callback.answer(
                f"{TEXTS['integrations']['status_updated']}: {changed_names}",
                show_alert=True,
            )
        else:
            await callback.answer()

    except Exception as e:
        # Handle errors gracefully - restore original keyboard
        from loguru import logger
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

        logger.error(f"Error refreshing status: {e}")

        # Restore original keyboard (remove loading state from refresh button)
        if old_keyboard and old_keyboard.inline_keyboard:
            restored_rows = []
            for row in old_keyboard.inline_keyboard:
                restored_row = []
                for button in row:
                    if button.callback_data == "refresh_status":
                        # Restore original refresh button
                        restored_row.append(
                            InlineKeyboardButton(
                                text=TEXTS["integrations"]["refresh_button"],
                                callback_data="refresh_status",
                            )
                        )
                    else:
                        restored_row.append(button)
                restored_rows.append(restored_row)
            restored_keyboard = InlineKeyboardMarkup(inline_keyboard=restored_rows)

            try:
                await callback.message.edit_reply_markup(reply_markup=restored_keyboard)
            except Exception:
                pass

        await callback.answer("Ошибка при обновлении статуса", show_alert=True)
