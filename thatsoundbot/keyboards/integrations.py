from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from thatsoundbot.handlers.messages.texts import TEXTS
from thatsoundbot.models import User
from thatsoundbot.settings import get_integrations, get_settings


def create_integrations_keyboard(
    user: User, htelegram_id: str, refresh_button_loading: bool = False
) -> InlineKeyboardMarkup:
    """Create inline keyboard with integration buttons."""
    buttons = []
    integrations_data = user.integrations.model_dump()
    settings = get_settings()

    for integration_config in get_integrations():
        name = integration_config["name"]
        if name not in integrations_data:
            continue

        enabled = integrations_data[name]
        display_name = integration_config["name"].capitalize()

        if enabled:
            button_text = f"{display_name}: подключено"
            buttons.append([InlineKeyboardButton(text=button_text, callback_data=f"integration:{name}:connected")])
        else:
            button_text = f"{display_name}: подключить"
            connect_url = integration_config["connect_url_template"].format(
                api_url=settings.API_URL, htelegram_id=htelegram_id
            )
            buttons.append([InlineKeyboardButton(text=button_text, url=connect_url)])

    # Add refresh status button after all integration buttons
    refresh_text = (
        TEXTS["integrations"]["refresh_button_loading"]
        if refresh_button_loading
        else TEXTS["integrations"]["refresh_button"]
    )
    buttons.append([InlineKeyboardButton(text=refresh_text, callback_data="refresh_status")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def update_integrations_keyboard(
    old_keyboard: InlineKeyboardMarkup | None,
    user: User,
    htelegram_id: str,
    refresh_button_loading: bool = False,
) -> InlineKeyboardMarkup:
    """Update only changed integration buttons in keyboard."""
    if not old_keyboard or not old_keyboard.inline_keyboard:
        # If no old keyboard, create new one
        return create_integrations_keyboard(user, htelegram_id, refresh_button_loading)

    new_integrations_data = user.integrations.model_dump()
    settings = get_settings()
    updated_buttons = []

    # Process integration buttons
    for row in old_keyboard.inline_keyboard:
        updated_row = []
        for button in row:
            # Skip refresh button, we'll add it at the end
            if button.callback_data == "refresh_status":
                continue

            # Check if this is an integration button with callback_data (connected)
            if button.callback_data and button.callback_data.startswith("integration:"):
                parts = button.callback_data.split(":")
                if len(parts) == 3:
                    integration_name = parts[1]
                    if integration_name in new_integrations_data:
                        enabled = new_integrations_data[integration_name]
                        display_name = integration_name.capitalize()

                        # Update button if status changed
                        if enabled:
                            # Still connected, check if text needs update
                            new_text = f"{display_name}: подключено"
                            new_callback = f"integration:{integration_name}:connected"
                            # Only update if text changed
                            if button.text != new_text:
                                updated_row.append(
                                    InlineKeyboardButton(text=new_text, callback_data=new_callback)
                                )
                            else:
                                updated_row.append(button)
                        else:
                            # Status changed: was connected, now disconnected - change to URL button
                            new_text = f"{display_name}: подключить"
                            # Find correct URL from integration config
                            connect_url = None
                            for integration_config in get_integrations():
                                if integration_config["name"] == integration_name:
                                    connect_url = integration_config["connect_url_template"].format(
                                        api_url=settings.API_URL, htelegram_id=htelegram_id
                                    )
                                    break

                            if connect_url:
                                updated_row.append(InlineKeyboardButton(text=new_text, url=connect_url))
                            else:
                                # Keep old button if URL not found
                                updated_row.append(button)
                    else:
                        # Integration not in new data, keep old button
                        updated_row.append(button)
                else:
                    updated_row.append(button)
            elif button.url:
                # This might be an integration URL button, check if it needs update
                integration_name = None
                for integration_config in get_integrations():
                    connect_url_template = integration_config["connect_url_template"]
                    expected_url = connect_url_template.format(
                        api_url=settings.API_URL, htelegram_id=htelegram_id
                    )
                    if button.url == expected_url:
                        integration_name = integration_config["name"]
                        break

                if integration_name and integration_name in new_integrations_data:
                    enabled = new_integrations_data[integration_name]
                    if enabled:
                        # Status changed to connected, update button
                        display_name = integration_name.capitalize()
                        new_text = f"{display_name}: подключено"
                        updated_row.append(
                            InlineKeyboardButton(text=new_text, callback_data=f"integration:{integration_name}:connected")
                        )
                    else:
                        # Still not connected, keep button
                        updated_row.append(button)
                else:
                    updated_row.append(button)
            else:
                # Not an integration button, keep as is
                updated_row.append(button)

        if updated_row:
            updated_buttons.append(updated_row)

    # Add refresh status button at the end
    refresh_text = (
        TEXTS["integrations"]["refresh_button_loading"]
        if refresh_button_loading
        else TEXTS["integrations"]["refresh_button"]
    )
    updated_buttons.append([InlineKeyboardButton(text=refresh_text, callback_data="refresh_status")])

    return InlineKeyboardMarkup(inline_keyboard=updated_buttons)
