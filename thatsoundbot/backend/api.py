from typing import Any

import httpx
from loguru import logger

from thatsoundbot.backend.client import APIClient, APIError
from thatsoundbot.settings import get_settings


async def mention_user(
    htelegram_id: str,
    client: APIClient | None = None,
) -> dict[str, Any]:
    """Get or create a user by hashed Telegram ID."""
    logger.info("Mention user", extra={"htelegram_id": htelegram_id})

    async def _make_request(client_to_use: APIClient) -> dict[str, Any]:
        """Make the API request with error handling."""
        try:
            result = await client_to_use.post(f"/api/v1/users/{htelegram_id}")
            logger.info(f"User mentioned: {result}")
            return result
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Failed to mention user: HTTP {e.response.status_code}",
                extra={"htelegram_id": htelegram_id, "status_code": e.response.status_code},
            )
            raise APIError(
                f"API request failed: {e.response.status_code}",
                status_code=e.response.status_code,
            ) from e
        except httpx.RequestError as e:
            logger.error(
                "Failed to mention user: request error",
                extra={"htelegram_id": htelegram_id},
            )
            raise APIError(f"API request failed: {str(e)}") from e

    # Use provided client or create a new one
    if client is None:
        settings = get_settings()
        async with APIClient(settings) as c:
            return await _make_request(c)

    return await _make_request(client)
