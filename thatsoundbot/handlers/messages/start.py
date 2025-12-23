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
        "connected": "подключено",
        "not_connected": "не подключено",
    },
}


def format_start_message(user: User, htelegram_id: str) -> str:
    """Format start command message based on user data."""
    is_new_user = user.message is not None

    label = (
        TEXTS["start"]["integrations_available"]
        if is_new_user
        else TEXTS["start"]["integrations_yours"]
    )

    integrations_data = user.integrations.model_dump()
    integrations_lines = []
    for name, enabled in integrations_data.items():
        status = (
            TEXTS["integrations"]["connected"]
            if enabled
            else TEXTS["integrations"]["not_connected"]
        )
        display_name = name.capitalize()
        integrations_lines.append(f"• {display_name}: {status}")

    integrations_text = f"{label}\n" + "\n".join(integrations_lines)

    if is_new_user:
        return f"{TEXTS['start']['welcome_new']} {integrations_text}"
    return f"{TEXTS['start']['welcome_returning']} {htelegram_id[:8]}.\n{integrations_text}"
