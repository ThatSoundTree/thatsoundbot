from pydantic import BaseModel


class SpotifyTokens(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str
    expires_at: int


class YandexToken(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    expires_at: int
    user_id: int | None = None
