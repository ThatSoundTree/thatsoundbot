from pydantic import BaseModel


class TrackView(BaseModel):
    """Track model for recently played tracks."""

    id: str
    name: str
    artists: list[str]
    album_cover_url: str | None = None
    played_at: str
    url: str


class RecentTracksView(BaseModel):
    """Response model for recently played tracks."""

    tracks: list[TrackView]
