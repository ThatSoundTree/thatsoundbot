from pydantic import BaseModel, ConfigDict

from thatsoundbot.settings import TSAPISettings


class TrackView(BaseModel):
    """Track model for recently played tracks."""

    model_config = ConfigDict(use_enum_values=True)

    id: str
    name: str
    artists: list[str]
    album_cover_url: str | None = None
    played_at: str | None = None
    url: str
    provider: TSAPISettings.Providers


class IntegrationsTracks(BaseModel):
    spotify: list[TrackView]
    yandex_music: list[TrackView]


class RecentTracksView(BaseModel):
    """Response model for recently played tracks."""

    tracks: IntegrationsTracks
