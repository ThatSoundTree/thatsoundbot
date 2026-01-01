from functools import lru_cache
from typing import TypedDict

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class IntegrationConfig(TypedDict):
    """Integration configuration."""

    name: str
    connect_url_template: str


class Settings(BaseSettings):
    """Telegram bot application settings"""

    TOKEN: SecretStr
    API_URL: str
    API_PUBLIC_URL: str = Field(description="Public URL for backend API (used in inline buttons)")
    TELEGRAM_HASH_KEY: SecretStr = Field(description="Secret key for hashing telegram_id to htelegram_id")
    TO_API_AUTH_KEY: SecretStr = Field(description="Auth key for authentication with thatsoundapi (sent as X-API-Key header)")
    DIRECT_API_URL: str
    TO_DIRECT_AUTH_KEY: SecretStr = Field(description="Auth key (Bearer token) for authentication with thatsounddirect API")
    TASK_STATUS_CHECK_INTERVAL: int = 10
    TEMP_FILE_CHANNEL: str

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
            "connect_url_template": "{api_public_url}/api/v1/spotify/login/{htelegram_id}",
        }
    ]
