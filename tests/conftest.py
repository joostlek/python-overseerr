"""Asynchronous Python client for Overseerr."""

from collections.abc import AsyncGenerator

import aiohttp
from aiointercept import aiointercept
import pytest

from python_overseerr import OverseerrClient
from syrupy import SnapshotAssertion

from .syrupy import OverseerrSnapshotExtension


@pytest.fixture(name="snapshot")
def snapshot_assertion(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return snapshot assertion fixture with the Overseerr extension."""
    return snapshot.use_extension(OverseerrSnapshotExtension)


@pytest.fixture
async def client() -> AsyncGenerator[OverseerrClient, None]:
    """Return a Overseerr client."""
    async with (
        aiohttp.ClientSession() as session,
        OverseerrClient(
            "overseerr.test",
            443,
            "key",
            session=session,
        ) as overseerr_client,
    ):
        yield overseerr_client


@pytest.fixture(name="responses")
async def aiointercept_fixture() -> AsyncGenerator[aiointercept, None]:
    """Return aiointercept fixture."""
    async with aiointercept(mock_external_urls=True) as mocked_responses:
        yield mocked_responses
