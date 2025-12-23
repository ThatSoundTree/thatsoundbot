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
        "status_updated": "Статус обновлен",
        "status_updating": "Обновление статуса...",
        "refresh_button": "⚙️ Обновить",
        "refresh_button_loading": "👀 Обновление...",
    },
}
