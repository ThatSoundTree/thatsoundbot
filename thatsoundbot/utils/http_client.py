from enum import StrEnum
from typing import Any
from urllib.parse import urlparse

import httpx
from loguru import logger


class MethodEnum(StrEnum):
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"


class HttpClient:

    @staticmethod
    async def __any_method(method: MethodEnum, url: str, **kwargs: Any) -> httpx.Response:
        logger.debug("{method} {url}", method=method, url=url)
        async with httpx.AsyncClient() as client:
            if method == MethodEnum.GET:
                response = await client.get(url, **kwargs)
            elif method == MethodEnum.POST:
                response = await client.post(url, **kwargs)
            elif method == MethodEnum.PATCH:
                response = await client.patch(url, **kwargs)
            else:
                raise NotImplementedError
        return response


    @staticmethod
    async def get(url: str, **kwargs: Any) -> httpx.Response:
        return await HttpClient.__any_method(method=MethodEnum.GET, url=url, **kwargs)

    @staticmethod
    async def post(url: str, **kwargs: Any) -> httpx.Response:
        return await HttpClient.__any_method(method=MethodEnum.POST, url=url, **kwargs)

    @staticmethod
    async def patch(url: str, **kwargs: Any) -> httpx.Response:
        return await HttpClient.__any_method(method=MethodEnum.PATCH, url=url, **kwargs)


def extract_domain(url: str) -> str:
    parsed_url = urlparse(url)
    return parsed_url.netloc
