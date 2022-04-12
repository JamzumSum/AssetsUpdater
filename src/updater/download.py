from os import PathLike
from pathlib import Path
from typing import AsyncGenerator, Awaitable, Callable, Optional

import aiofiles
import aiohttp
from aiohttp.typedefs import StrOrURL
from yarl import URL

__all__ = ["download"]


async def aaccint(it: AsyncGenerator[int, None]):
    acc = 0
    async for i in it:
        acc += i
        yield acc


async def download(
    url: StrOrURL,
    local: Optional[PathLike] = None,
    buffer: int = 8192,
    echo_progress: Optional[Callable[[int], Awaitable]] = None,
    **get_kw,
):
    """async-download a url to a the given path.

    :param local: where to download
    :param echo_progress: async function to receive downloaded size as a int.

    :return: size
    """
    url = url if isinstance(url, URL) else URL(url)
    local = Path(local or url.name)
    local.parent.mkdir(parents=True, exist_ok=True)
    assert not local.is_dir(), "destination should not be a directory"

    acc = 0
    async with aiohttp.ClientSession() as sess, aiofiles.open(local, "wb") as f:
        async with sess.get(url, **get_kw) as r:
            it = r.content.iter_chunked(buffer)
            async for c in it:
                if c:
                    acc += await f.write(c)
                    if echo_progress:
                        await echo_progress(acc)

    return acc
