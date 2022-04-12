import pytest

from updater.github import GhUpdater
from updater.utils import get_latest_asset
from updater.utils import version_filter

pytestmark = pytest.mark.asyncio


async def test_latest_asset(up: GhUpdater):
    url = await get_latest_asset(up, "emoji.db")
    assert url.download_url


@pytest.mark.xfail
async def test_latest_asset_FN(up):
    await get_latest_asset(up, "QAQ")


async def test_version_filter(up):
    rels = version_filter(up, ">=0.0.1", num=3, pre=True)
    l = [i async for i in rels]
    assert l
