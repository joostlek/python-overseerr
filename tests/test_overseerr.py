"""Tests for the client."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import aiohttp
from aiohttp import ClientError
from aiohttp.hdrs import METH_GET, METH_POST
from aioresponses import CallbackResult, aioresponses
import pytest

from python_overseerr import OverseerrClient
from python_overseerr.exceptions import OverseerrConnectionError, OverseerrError
from python_overseerr.models import (
    NotificationType,
    RequestFilterStatus,
    RequestSortStatus,
)
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


@pytest.mark.parametrize(
    ("endpoint", "fixture", "method"),
    [
        ("request/count", "request_count.json", "get_request_count"),
        ("status", "status.json", "get_status"),
        (
            "settings/notifications/webhook",
            "webhook_config.json",
            "get_webhook_notification_config",
        ),
    ],
    ids=[
        "request_count",
        "status",
        "webhook_config",
    ],
)
async def test_data_retrieval(
    responses: aioresponses,
    client: OverseerrClient,
    snapshot: SnapshotAssertion,
    endpoint: str,
    fixture: str,
    method: str,
) -> None:
    """Test data retrieval."""
    responses.get(
        f"{MOCK_URL}/{endpoint}",
        status=200,
        body=load_fixture(fixture),
    )
    assert await getattr(client, method)() == snapshot
    responses.assert_called_once_with(
        f"{MOCK_URL}/{endpoint}",
        METH_GET,
        headers=HEADERS,
        params=None,
        json=None,
    )


@pytest.mark.parametrize(
    "fixtures",
    [
        "search_1.json",
        "search_2.json",
    ],
)
async def test_search(
    responses: aioresponses,
    client: OverseerrClient,
    snapshot: SnapshotAssertion,
    fixtures: str,
) -> None:
    """Test searching for media."""
    responses.get(
        f"{MOCK_URL}/search?query=frosty",
        status=200,
        body=load_fixture(fixtures),
    )
    assert await client.search("frosty") == snapshot
    responses.assert_called_once_with(
        f"{MOCK_URL}/search",
        METH_GET,
        headers=HEADERS,
        params={"query": "frosty"},
        json=None,
    )


async def test_setting_webhook_configuration(
    responses: aioresponses,
    client: OverseerrClient,
) -> None:
    """Test setting webhook configuration."""
    responses.post(
        f"{MOCK_URL}/settings/notifications/webhook",
        status=200,
    )
    await client.set_webhook_notification_config(
        enabled=True,
        types=NotificationType.REQUEST_APPROVED,
        webhook_url="http://localhost",
        json_payload="{}",
    )
    responses.assert_called_once_with(
        f"{MOCK_URL}/settings/notifications/webhook",
        METH_POST,
        headers=HEADERS,
        params=None,
        json={
            "enabled": True,
            "types": 4,
            "options": {
                "webhookUrl": "http://localhost",
                "jsonPayload": "{}",
            },
        },
    )


async def test_webhook_config_test(
    responses: aioresponses,
    client: OverseerrClient,
) -> None:
    """Test setting webhook configuration."""
    responses.post(
        f"{MOCK_URL}/settings/notifications/webhook/test",
        status=204,
    )
    assert (
        await client.test_webhook_notification_config(
            webhook_url="http://localhost",
            json_payload="{}",
        )
        is True
    )
    responses.assert_called_once_with(
        f"{MOCK_URL}/settings/notifications/webhook/test",
        METH_POST,
        headers=HEADERS,
        params=None,
        json={
            "enabled": True,
            "types": 2,
            "options": {
                "webhookUrl": "http://localhost",
                "jsonPayload": "{}",
            },
        },
    )


async def test_failing_webhook_config_test(
    responses: aioresponses,
    client: OverseerrClient,
) -> None:
    """Test setting webhook configuration."""
    responses.post(
        f"{MOCK_URL}/settings/notifications/webhook/test",
        status=500,
        body='{"message": "Failed to send webhook notification."}',
    )
    assert (
        await client.test_webhook_notification_config(
            webhook_url="http://localhost",
            json_payload="{}",
        )
        is False
    )
    responses.assert_called_once_with(
        f"{MOCK_URL}/settings/notifications/webhook/test",
        METH_POST,
        headers=HEADERS,
        params=None,
        json={
            "enabled": True,
            "types": 2,
            "options": {
                "webhookUrl": "http://localhost",
                "jsonPayload": "{}",
            },
        },
    )


async def test_fetching_requests(
    responses: aioresponses,
    client: OverseerrClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test fetching requests."""
    responses.get(
        f"{MOCK_URL}/request",
        status=200,
        body=load_fixture("request.json"),
    )
    assert await client.get_requests() == snapshot
    responses.assert_called_once_with(
        f"{MOCK_URL}/request", METH_GET, headers=HEADERS, params={}, json=None
    )


@pytest.mark.parametrize(
    ("kwargs", "params", "query_string"),
    [
        ({"status": RequestFilterStatus.ALL}, {"filter": "all"}, "filter=all"),
        ({"sort": RequestSortStatus.ADDED}, {"sort": "added"}, "sort=added"),
        ({"requested_by": 1}, {"requestedBy": 1}, "requestedBy=1"),
    ],
)
async def test_fetching_request_parameters(
    responses: aioresponses,
    client: OverseerrClient,
    kwargs: dict[str, Any],
    params: dict[str, Any],
    query_string: str,
) -> None:
    """Test fetching requests with parameters."""
    responses.get(
        f"{MOCK_URL}/request?{query_string}",
        status=200,
        body=load_fixture("request.json"),
    )
    await client.get_requests(**kwargs)
    responses.assert_called_once_with(
        f"{MOCK_URL}/request", METH_GET, headers=HEADERS, params=params, json=None
    )
