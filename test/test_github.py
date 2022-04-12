import pytest

from updater.github import GhUpdater

pytestmark = pytest.mark.asyncio


async def test_latest(up: GhUpdater):
    r = await up.latest()
    assert r
    assert r.tag
    assert r.title


async def test_asset(up: GhUpdater):
    r = await up.latest()
    assert r
    a = r.assets()
    assert a
    f = list(filter(lambda i: i.name == "emoji.db", a))
    assert len(f) == 1
    a = f[0]
    del f
    assert a.download_url


async def test_all(up: GhUpdater):
    r = await up.all(None, True)
    assert r
