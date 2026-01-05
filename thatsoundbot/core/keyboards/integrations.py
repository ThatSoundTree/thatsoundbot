from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from thatsoundbot.core.handlers.messages.texts import TEXTS
from thatsoundbot.core.models import User
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
                api_public_url=settings.API_PUBLIC_URL, htelegram_id=htelegram_id
            )
            buttons.append([InlineKeyboardButton(text=button_text, url=connect_url)])

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
        return create_integrations_keyboard(user, htelegram_id, refresh_button_loading)

    new_integrations_data = user.integrations.model_dump()
    settings = get_settings()
    updated_buttons = []

    for row in old_keyboard.inline_keyboard:
        updated_row = []
        for button in row:
            if button.callback_data == "refresh_status":
                continue

            if button.callback_data and button.callback_data.startswith("integration:"):
                parts = button.callback_data.split(":")
                if len(parts) == 3:
                    integration_name = parts[1]
                    if integration_name in new_integrations_data:
                        enabled = new_integrations_data[integration_name]
                        display_name = integration_name.capitalize()

                        if enabled:
                            new_text = f"{display_name}: подключено"
                            new_callback = f"integration:{integration_name}:connected"
                            if button.text != new_text:
                                updated_row.append(
                                    InlineKeyboardButton(text=new_text, callback_data=new_callback)
                                )
                            else:
                                updated_row.append(button)
                        else:
                            new_text = f"{display_name}: подключить"
                            connect_url = None
                            for integration_config in get_integrations():
                                if integration_config["name"] == integration_name:
                                    connect_url = integration_config["connect_url_template"].format(
                                        api_public_url=settings.API_PUBLIC_URL, htelegram_id=htelegram_id
                                    )
                                    break

                            if connect_url:
                                updated_row.append(InlineKeyboardButton(text=new_text, url=connect_url))
                            else:
                                updated_row.append(button)
                    else:
                        updated_row.append(button)
                else:
                    updated_row.append(button)
            elif button.url:
                integration_name = None
                for integration_config in get_integrations():
                    connect_url_template = integration_config["connect_url_template"]
                    expected_url = connect_url_template.format(
                        api_public_url=settings.API_PUBLIC_URL, htelegram_id=htelegram_id
                    )
                    if button.url == expected_url:
                        integration_name = integration_config["name"]
                        break

                if integration_name and integration_name in new_integrations_data:
                    enabled = new_integrations_data[integration_name]
                    if enabled:
                        display_name = integration_name.capitalize()
                        new_text = f"{display_name}: подключено"
                        updated_row.append(
                            InlineKeyboardButton(text=new_text, callback_data=f"integration:{integration_name}:connected")
                        )
                    else:
                        updated_row.append(button)
                else:
                    updated_row.append(button)
            else:
                updated_row.append(button)

        if updated_row:
            updated_buttons.append(updated_row)

    refresh_text = (
        TEXTS["integrations"]["refresh_button_loading"]
        if refresh_button_loading
        else TEXTS["integrations"]["refresh_button"]
    )
    updated_buttons.append([InlineKeyboardButton(text=refresh_text, callback_data="refresh_status")])

    return InlineKeyboardMarkup(inline_keyboard=updated_buttons)
