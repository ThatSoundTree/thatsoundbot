from functools import lru_cache
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Telegram bot application settings"""

    TOKEN: SecretStr

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore", env_prefix="TELEGRAM_BOT_"
    )


@lru_cache()
def get_settings() -> Settings:
    """Cached settings function"""
    return Settings()  # type: ignore[call-arg]
