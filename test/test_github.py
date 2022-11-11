import pytest
from httpx import AsyncClient

from updater.github import GhUpdater

pytestmark = pytest.mark.asyncio


async def test_latest(up: GhUpdater):
    r = await up.latest()
    assert r
    assert isinstance(r.tag, str)
    assert isinstance(r.title, str)
    assert isinstance(r.body, str)
    assert isinstance(r.pre, bool)
    assert r.draft is False


async def test_asset(up: GhUpdater):
    r = await up.latest()
    assert r
    a = r.assets()
    assert a
    f = list(filter(lambda i: i.name == "emoji.db", a))
    if len(f) == 1:
        a = f[0]
        assert isinstance(a.download_url, str)
        assert a.from_release is r


async def test_all(up: GhUpdater):
    r = await up.all(None, True)
    assert r


async def test_not_exist(client: AsyncClient):
    from updater.exc import ReleaseNotFound

    up = GhUpdater(client, "JamzumSum", "abab")
    with pytest.raises(ReleaseNotFound):
        await up.latest(True)
