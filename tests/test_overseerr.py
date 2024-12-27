"""Tests for the client."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import aiohttp
from aiohttp import ClientError
from aiohttp.hdrs import METH_GET
from aioresponses import CallbackResult, aioresponses
import pytest

from python_overseerr import OverseerrClient
from python_overseerr.exceptions import OverseerrConnectionError, OverseerrError
from tests import load_fixture
from tests.const import HEADERS, MOCK_URL

if TYPE_CHECKING:
    from syrupy import SnapshotAssertion


async def test_putting_in_own_session(
    responses: aioresponses,
) -> None:
    """Test putting in own session."""
    responses.get(
        f"{MOCK_URL}/request/count",
        status=200,
        body=load_fixture("request_count.json"),
    )
    async with aiohttp.ClientSession() as session:
        overseerr = OverseerrClient("192.168.0.30", 443, "abc", session=session)
        await overseerr.get_request_count()
        assert overseerr.session is not None
        assert not overseerr.session.closed
        await overseerr.close()
        assert not overseerr.session.closed


async def test_creating_own_session(
    responses: aioresponses,
) -> None:
    """Test creating own session."""
    responses.get(
        f"{MOCK_URL}/request/count",
        status=200,
        body=load_fixture("request_count.json"),
    )
    overseerr = OverseerrClient("192.168.0.30", 443, "abc")
    await overseerr.get_request_count()
    assert overseerr.session is not None
    assert not overseerr.session.closed
    await overseerr.close()
    assert overseerr.session.closed


async def test_unexpected_server_response(
    responses: aioresponses,
    client: OverseerrClient,
) -> None:
    """Test handling unexpected response."""
    responses.get(
        f"{MOCK_URL}/request/count",
        status=404,
        headers={"Content-Type": "plain/text"},
        body="Yes",
    )
    with pytest.raises(OverseerrError):
        await client.get_request_count()


async def test_timeout(
    responses: aioresponses,
) -> None:
    """Test request timeout."""

    # Faking a timeout by sleeping
    async def response_handler(_: str, **_kwargs: Any) -> CallbackResult:
        """Response handler for this test."""
        await asyncio.sleep(2)
        return CallbackResult(body="Goodmorning!")

    responses.get(
        f"{MOCK_URL}/request/count",
        callback=response_handler,
    )
    async with OverseerrClient(
        "192.168.0.30",
        443,
        "abc",
        request_timeout=1,
    ) as overseerr:
        with pytest.raises(OverseerrConnectionError):
            await overseerr.get_request_count()


async def test_client_error(
    client: OverseerrClient,
    responses: aioresponses,
) -> None:
    """Test client error."""

    async def response_handler(_: str, **_kwargs: Any) -> CallbackResult:
        """Response handler for this test."""
        raise ClientError

    responses.get(
        f"{MOCK_URL}/measures/current",
        callback=response_handler,
    )
    with pytest.raises(OverseerrConnectionError):
        await client.get_request_count()


async def test_request_count(
    responses: aioresponses,
    client: OverseerrClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test getting request count."""
    responses.get(
        f"{MOCK_URL}/request/count",
        status=200,
        body=load_fixture("request_count.json"),
    )
    assert await client.get_request_count() == snapshot
    responses.assert_called_once_with(
        f"{MOCK_URL}/request/count",
        METH_GET,
        headers=HEADERS,
        json=None,
    )
