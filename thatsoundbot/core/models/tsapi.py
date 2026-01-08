from pydantic import BaseModel


class TrackView(BaseModel):
    """Track model for recently played tracks."""

    id: str
    name: str
    artists: list[str]
    album_cover_url: str | None = None
    played_at: str | None = None
    url: str


class IntegrationsTracks(BaseModel):
    spotify: list[TrackView]
    yandex_music: list[TrackView]


class RecentTracksView(BaseModel):
    """Response model for recently played tracks."""

    tracks: IntegrationsTracks
