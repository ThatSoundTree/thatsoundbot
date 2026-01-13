import json
from enum import Enum
from functools import lru_cache
from typing import TypedDict
from urllib.parse import quote_plus

from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from thatsoundbot.core.models.pipelines_view import PipelinesView


class IntegrationConfig(TypedDict):
    """Integration configuration."""

    name: str
    connect_url_template: str


class Settings(BaseSettings):
    """Telegram bot application settings"""

    LOG_LEVEL: str = "INFO"

    TOKEN: SecretStr
    HASH_KEY: SecretStr = Field(description="Secret key for hashing telegram_id to htelegram_id")
    PIPELINES_PATH: str = Field(default="pipelines.json", description="Path to pipelines.json file")

    LOGS_CHANNEL_URL: str
    CACHE_CHANNEL: str

    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = Field(default=6379, ge=1, le=65535)
    REDIS_DB: int = Field(default=0, ge=0)
    REDIS_USERNAME: str | None = None
    REDIS_PASSWORD: SecretStr | None = None
    REDIS_RESULT_TTL: int = Field(default=300)

    FETCH_FILE_ATTEMPTS: int = Field(default=10)
    FETCH_FILE_SLEEP_TIME: int = Field(default=5)


    @computed_field  # type: ignore[prop-decorator]
    @property
    def REDIS_URL(self) -> str:
        """Auto assembling redis url with URL encoding"""
        host = self.REDIS_HOST
        port = self.REDIS_PORT
        db = self.REDIS_DB

        if self.REDIS_USERNAME and self.REDIS_PASSWORD:
            username = quote_plus(self.REDIS_USERNAME)
            password = quote_plus(self.REDIS_PASSWORD.get_secret_value())
            return f"redis://{username}:{password}@{host}:{port}/{db}"
        elif self.REDIS_USERNAME:
            username = quote_plus(self.REDIS_USERNAME)
            return f"redis://{username}@{host}:{port}/{db}"
        elif self.REDIS_PASSWORD:
            password = quote_plus(self.REDIS_PASSWORD.get_secret_value())
            return f"redis://:{password}@{host}:{port}/{db}"
        return f"redis://{host}:{port}/{db}"

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore", env_prefix="TELEGRAM_BOT_"
    )



class TSAPISettings(BaseSettings):
    """Telegram bot application settings"""
    BASE_URL: str
    AUTH_KEY: str

    SPOTIFY_AUTH_TEMPLATE: str
    YANDEX_AUTH_TEMPLATE: str

    def get_header(self) -> dict:
        return {
            "Authorization": f"Bearer {self.AUTH_KEY}",
        }

    def get_auth_urls(self, hgramid: str):
        return {
            "spotify": self.SPOTIFY_AUTH_TEMPLATE.format(hgramid=hgramid),
            "YandexMusic": self.YANDEX_AUTH_TEMPLATE.format(hgramid=hgramid),
        }

    class Providers(Enum):
        Spotify = 1
        YandexMusic = 2

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore", env_prefix="TSAPI_"
    )

class TSRipperSettings(BaseSettings):
    """Something in the way."""

    BASE_URL: str
    IN_USE: bool = Field(default=False)
    SCROBBLE_SLEEP_TIME: int = Field(default=3)
    ATTEMPTS: int = Field(default=5)

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore", env_prefix="TSRIPPER_"
    )


@lru_cache()
def get_settings() -> Settings:
    """Cached settings function"""
    return Settings()  # type: ignore[call-arg]


@lru_cache()
def get_tsapi_settings() -> TSAPISettings:
    return TSAPISettings()  # type: ignore[call-arg]


@lru_cache()
def get_tsripper_settings() -> TSRipperSettings:
    return TSRipperSettings()  # type: ignore[call-arg]

@lru_cache()
def get_pipelines() -> PipelinesView:
    with open(get_settings().PIPELINES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return PipelinesView.model_validate(data)
