import httpx

from thatsoundbot.settings import get_settings


class TSDirectHTTPClient:
    """HTTP client for making authenticated requests to TSDirect API with Bearer token."""

    @staticmethod
    def _get_auth_headers() -> dict[str, str]:
        """Get authorization headers with Bearer token."""
        settings = get_settings()
        return {
            "Authorization": f"Bearer {settings.TSDIRECT_SECRET_KEY.get_secret_value()}",
        }

    @staticmethod
    async def post(url: str, **kwargs) -> httpx.Response:
        """Make authenticated POST request to TSDirect API."""
        headers = TSDirectHTTPClient._get_auth_headers()
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, **kwargs)
            return response

    @staticmethod
    async def get(url: str, **kwargs) -> httpx.Response:
        """Make authenticated GET request to TSDirect API."""
        headers = TSDirectHTTPClient._get_auth_headers()
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, **kwargs)
            return response
