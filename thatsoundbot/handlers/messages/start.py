from aiogram.types import InlineKeyboardMarkup

from thatsoundbot.keyboards.integrations import create_integrations_keyboard
from thatsoundbot.models import User

# TODO: Add multi-language support in the future
# Structure: LANGUAGES = {"ru": {...}, "en": {...}}
# Then use: texts = LANGUAGES.get(user_language, LANGUAGES["ru"])


TEXTS = {
    "start": {
        "welcome_new": "Добро пожаловать,",
        "welcome_returning": "Привет снова,",
        "integrations_available": "в боте доступны следующие интеграции:",
        "integrations_yours": "Твои интеграции:",
    },
    "integrations": {
        "connected_alert": "И это замечательно!",
    },
}


def format_start_message(
    user: User, htelegram_id: str
) -> tuple[str, InlineKeyboardMarkup]:
    """Format start command message based on user data.

    Returns:
        tuple[str, InlineKeyboardMarkup]: Message text and inline keyboard.
    """
    is_new_user = user.message is not None

    label = (
        TEXTS["start"]["integrations_available"]
        if is_new_user
        else TEXTS["start"]["integrations_yours"]
    )

    if is_new_user:
        message_text = f"{TEXTS['start']['welcome_new']}\n{label}"
    else:
        message_text = f"{TEXTS['start']['welcome_returning']} {htelegram_id[:8]}.\n{label}"

    keyboard = create_integrations_keyboard(user, htelegram_id)

    return message_text, keyboard
