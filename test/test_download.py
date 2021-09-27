from pathlib import Path

import pytest
import updater
from updater.download import adownload, download
from updater.github import GhUpdater, Repo

url = local = PRXOY = None

try:
    import aiofiles
    import aiohttp
    hasaio = True
except ImportError:
    hasaio = False
needaio = pytest.mark.skipif(hasaio, reason='aiohttp not installed')


def setup():
    global url, local, PROXY
    up = GhUpdater(Repo('JamzumSum', 'QzEmoji'))
    asset = updater.get_latest_asset(up, 'emoji.db')
    assert asset.download_url
    url = asset.download_url

    local = Path('tmp/emoji.db')
    local.unlink(missing_ok=True)

    from os import environ as env
    PROXY = env.get('HTTPS_PROXY', None)


def test_download():
    for i in download(url, local, proxies={'https': PROXY}):
        print(i, end='->')


@needaio
def test_adownload():
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(adownload(url, local))
