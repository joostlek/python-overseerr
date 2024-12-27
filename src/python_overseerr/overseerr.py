"""Asynchronous Python client for Overseerr."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from importlib import metadata
import socket
from typing import TYPE_CHECKING, Any

from aiohttp import ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from .exceptions import OverseerrConnectionError
from .models import RequestCount

if TYPE_CHECKING:
    from typing_extensions import Self


VERSION = metadata.version(__package__)


@dataclass
class OverseerrClient:
    """Main class for handling connections with Overseerr."""

    host: str
    port: int
    api_key: str
    ssl: bool = True
    session: ClientSession | None = None
    request_timeout: int = 10
    _close_session: bool = False

    async def _request(
        self,
        method: str,
        uri: str,
        *,
        data: dict[str, Any] | None = None,
    ) -> str:
        """Handle a request to Overseerr."""
        url = URL.build(
            host=self.host, port=self.port, scheme="https" if self.ssl else "http"
        ).joinpath(f"api/v1/{uri}")

        headers = {
            "User-Agent": f"PythonOverseerr/{VERSION}",
            "Accept": "application/json",
            "X-Api-Key": self.api_key,
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    headers=headers,
                    json=data,
                )
        except asyncio.TimeoutError as exception:
            msg = "Timeout occurred while connecting to the service"
            raise OverseerrConnectionError(msg) from exception
        except (
            ClientError,
            ClientResponseError,
            socket.gaierror,
        ) as exception:
            msg = "Error occurred while communicating with the service"
            raise OverseerrConnectionError(msg) from exception

        if response.status != 200:
            content_type = response.headers.get("Content-Type", "")
            text = await response.text()
            msg = "Unexpected response from Overseerr"
            raise OverseerrConnectionError(
                msg,
                {"Content-Type": content_type, "response": text},
            )

        return await response.text()

    async def get_request_count(self) -> RequestCount:
        """Get request count from Overseerr."""
        response = await self._request(METH_GET, "request/count")
        return RequestCount.from_json(response)

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The OverseerrClient object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()
