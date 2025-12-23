from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from thatsoundbot.models import User
from thatsoundbot.settings import get_integrations, get_settings


def create_integrations_keyboard(user: User, htelegram_id: str) -> InlineKeyboardMarkup:
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

    return InlineKeyboardMarkup(inline_keyboard=buttons)
