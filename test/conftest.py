import asyncio

import pytest
import pytest_asyncio
from aiohttp import ClientSession

from updater.github import GhUpdater


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def sess():
    async with ClientSession() as sess:
        yield sess


@pytest.fixture(scope="module")
def up(sess):
    return GhUpdater(sess, "JamzumSum", "QzEmoji")
