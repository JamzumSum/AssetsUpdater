import asyncio

import pytest
import pytest_asyncio
from httpx import AsyncClient

from updater.github import GhUpdater


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def client():
    async with AsyncClient() as client:
        yield client


@pytest.fixture(scope="module")
def up(client: AsyncClient):
    return GhUpdater(client, "aioqzone", "QzEmoji")
