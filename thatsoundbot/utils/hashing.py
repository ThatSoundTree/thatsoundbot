import base64
import hashlib
import hmac
import json

from thatsoundbot.settings import get_settings


def hash_telegram_id(telegram_id: int | str) -> str:
    """Hash telegram_id using TELEGRAM_HASH_KEY from settings."""
    secret_key = get_settings().TELEGRAM_HASH_KEY.get_secret_value()
    return hmac.new(
        secret_key.encode(),
        str(telegram_id).encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()
