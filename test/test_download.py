from pathlib import Path

import pytest

from updater.download import adownload
from updater.download import download
from updater.github import GhUpdater
from updater.github import Repo
import updater.utils as updater


@pytest.fixture(scope="module")
def local():
    i = Path("tmp/emoji.db")
    if i.exists():
        i.unlink()
    return i


@pytest.fixture(scope="module")
def url():
    up = GhUpdater(Repo("JamzumSum", "QzEmoji"))
    asset = updater.get_latest_asset(up, "emoji.db")
    assert asset.download_url
    return asset.download_url


@pytest.fixture(scope="module")
def PROXY():
    from os import environ as env

    return env.get("HTTPS_PROXY", None)


def test_download(url, local, PROXY):
    for i in download(url, local, proxies={"https": PROXY}):
        print(i, end="->")


@pytest.mark.asyncio
async def test_adownload(url, local, PROXY):
    try:
        import aiofiles
        import aiohttp
    except ImportError:
        pytest.skip("aiohttp/aiofiles not installed")

    await adownload(url, local, proxy=PROXY)
