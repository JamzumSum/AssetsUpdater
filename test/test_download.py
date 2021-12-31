from pathlib import Path

import pytest
import updater.utils as updater
from updater.download import adownload, download
from updater.github import GhUpdater, Repo

try:
    import aiofiles
    import aiohttp
    hasaio = True
except ImportError:
    hasaio = False
needaio = pytest.mark.skipif(not hasaio, reason='aiohttp/aiofiles not installed')


@pytest.fixture(scope='module')
def local():
    i = Path('tmp/emoji.db')
    i.unlink(missing_ok=True)
    return i


@pytest.fixture(scope='module')
def url():
    up = GhUpdater(Repo('JamzumSum', 'QzEmoji'))
    asset = updater.get_latest_asset(up, 'emoji.db')
    assert asset.download_url
    return asset.download_url


@pytest.fixture(scope='module')
def PROXY():
    from os import environ as env
    return env.get('HTTPS_PROXY', None)


def test_download(url, local, PROXY):
    for i in download(url, local, proxies={'https': PROXY}):
        print(i, end='->')


@needaio
def test_adownload(url, local):
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(adownload(url, local))
z