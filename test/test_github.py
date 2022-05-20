import pytest
from aiohttp import ClientSession

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


async def test_not_exist(sess: ClientSession):
    from updater.exc import ReleaseNotFound

    up = GhUpdater(sess, "JamzumSum", "abab")
    with pytest.raises(ReleaseNotFound):
        await up.latest(True)
