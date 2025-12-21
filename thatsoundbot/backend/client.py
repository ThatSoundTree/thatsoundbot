from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from thatsoundbot.settings import Settings

T = TypeVar("T", bound=BaseModel)


class APIError(Exception):
    """Exception for API-related errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class APIClient:
    """Simple async API client."""

    def __init__(self, settings: Settings) -> None:
        self.base_url = settings.API_URL.rstrip("/")
        self.api_key = settings.API_KEY.get_secret_value()
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "APIClient":
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={"X-API-Key": self.api_key},
        )
        return self

    async def __aexit__(self, exc_type: type, exc_val: Exception, exc_tb: object) -> None:
        if self._client:
            await self._client.aclose()

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        json: dict[str, Any] | BaseModel | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make HTTP request."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        # Use relative endpoint - httpx will automatically concatenate with base_url
        url = endpoint.lstrip("/")
        json_data = json.model_dump(exclude_none=True) if isinstance(json, BaseModel) else json

        response = await self._client.request(method=method, url=url, json=json_data, params=params)
        response.raise_for_status()
        return response.json() if response.content else {}

    async def get(
        self,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        response_model: type[T] | None = None,
    ) -> T | dict[str, Any]:
        """Make GET request."""
        data = await self._request("GET", endpoint, params=params)
        return response_model.model_validate(data) if response_model else data

    async def post(
        self,
        endpoint: str,
        *,
        json: dict[str, Any] | BaseModel | None = None,
        response_model: type[T] | None = None,
    ) -> T | dict[str, Any]:
        """Make POST request."""
        data = await self._request("POST", endpoint, json=json)
        return response_model.model_validate(data) if response_model else data

    async def put(
        self,
        endpoint: str,
        *,
        json: dict[str, Any] | BaseModel | None = None,
        response_model: type[T] | None = None,
    ) -> T | dict[str, Any]:
        """Make PUT request."""
        data = await self._request("PUT", endpoint, json=json)
        return response_model.model_validate(data) if response_model else data

    async def delete(
        self,
        endpoint: str,
        *,
        response_model: type[T] | None = None,
    ) -> T | dict[str, Any]:
        """Make DELETE request."""
        data = await self._request("DELETE", endpoint)
        return response_model.model_validate(data) if response_model else data
