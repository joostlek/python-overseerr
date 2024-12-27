"""Asynchronous Python client for Overseerr."""

from collections.abc import AsyncGenerator, Generator

import aiohttp
from aioresponses import aioresponses
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
            "192.168.0.30",
            443,
            "key",
            session=session,
        ) as overseerr_client,
    ):
        yield overseerr_client


@pytest.fixture(name="responses")
def aioresponses_fixture() -> Generator[aioresponses, None, None]:
    """Return aioresponses fixture."""
    with aioresponses() as mocked_responses:
        yield mocked_responses
