import itertools
from pathlib import Path
from typing import AsyncIterable, Callable, Union

import requests

from .type import Url


def download(url: Url, local: Union[str, Path], buffer: int = 8192, **kwargs):
    if isinstance(local, str): local = Path(local)
    local.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, stream=True, **kwargs)
    with open(local, 'wb') as f:
        dl_size = (f.write(c) for c in r.iter_content(buffer) if c)
        yield from itertools.accumulate(dl_size)


async def aaccint(it: AsyncIterable[int]):
    acc = 0
    async for i in it:
        acc += i
        yield acc


async def adownload(
    url: Url,
    local: Union[str, Path],
    buffer: int = 8192,
    acc_callback: Callable[[int], None] = None,
    **kwargs
):
    import aiofiles
    import aiohttp
    if isinstance(local, str): local = Path(local)
    local.parent.mkdir(parents=True, exist_ok=True)

    async with aiohttp.ClientSession() as sess:
        async with aiofiles.open(local, 'wb') as af:
            async with sess.get(url, **kwargs) as r:
                ait = r.content.iter_chunked(buffer)
                dl_size = (await af.write(c) async for c in ait if c)
                async for i in aaccint(dl_size):
                    if acc_callback: acc_callback(i)


__all__ = [i.__name__ for i in [
    download,
    adownload,
]]
