import json
from functools import lru_cache
from typing import TypedDict

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from thatsoundbot.core.models.pipelines_view import PipelinesView


class IntegrationConfig(TypedDict):
    """Integration configuration."""

    name: str
    connect_url_template: str


class Settings(BaseSettings):
    """Telegram bot application settings"""

    TOKEN: SecretStr
    HASH_KEY: SecretStr = Field(description="Secret key for hashing telegram_id to htelegram_id")
    PIPELINES_PATH: str = Field(default="pipelines.json", description="Path to pipelines.json file")

    LOGS_CHANNEL_URL: str
    USE_TSRIPPER: bool = Field(default=False)

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore", env_prefix="TELEGRAM_BOT_"
    )


class TSAPISettings(BaseSettings):
    """Telegram bot application settings"""
    BASE_URL: str
    AUTH_KEY: str

    SPOTIFY_AUTH_TEMPLATE: str

    def get_header(self) -> dict:
        return {
            "Authorization": f"Bearer {self.AUTH_KEY}",
        }

    def get_auth_urls(self, hgramid: str):
        return {
            "spotify": self.SPOTIFY_AUTH_TEMPLATE.format(hgramid=hgramid),
        }

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore", env_prefix="TSAPI_"
    )


@lru_cache()
def get_settings() -> Settings:
    """Cached settings function"""
    return Settings()  # type: ignore[call-arg]


@lru_cache()
def get_tsapi_settings() -> TSAPISettings:
    return TSAPISettings()  # type: ignore[call-arg]


@lru_cache()
def get_pipelines() -> PipelinesView:
    with open(get_settings().PIPELINES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return PipelinesView.model_validate(data)
