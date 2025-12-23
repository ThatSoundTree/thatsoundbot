from functools import lru_cache
from typing import TypedDict

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class IntegrationConfig(TypedDict):
    """Integration configuration."""

    name: str
    connect_url_template: str


class Settings(BaseSettings):
    """Telegram bot application settings"""

    TOKEN: SecretStr
    API_URL: str
    SECRET_KEY: SecretStr
    API_KEY: SecretStr

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore", env_prefix="TELEGRAM_BOT_"
    )


@lru_cache()
def get_settings() -> Settings:
    """Cached settings function"""
    return Settings()  # type: ignore[call-arg]


def get_integrations() -> list[IntegrationConfig]:
    """List of available integrations."""
    return [
        {
            "name": "spotify",
            "connect_url_template": "{api_url}/api/v1/spotify/login/{htelegram_id}",
        }
    ]
