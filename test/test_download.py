from pathlib import Path

import pytest
import pytest_asyncio

from updater.download import download
from updater.github import GhUpdater
import updater.utils as updater

pytestmark = pytest.mark.asyncio


@pytest.fixture
def local():
    i = Path("tmp/emoji.db")
    if i.exists():
        i.unlink()
    return i


@pytest_asyncio.fixture(scope="module")
async def url(up: GhUpdater):
    asset = await updater.get_latest_asset(up, "emoji.db")
    assert asset.download_url
    return asset.download_url


async def test_download(url: str, local: Path):
    await download(url, local)
