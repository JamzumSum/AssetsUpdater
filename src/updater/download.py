import asyncio
import logging
from os import PathLike
from pathlib import Path
from typing import Awaitable, Callable, Optional

import aiofiles
import aiohttp
from aiohttp.typedefs import StrOrURL
from yarl import URL

log = logging.getLogger(__name__)

__all__ = ["download"]


async def download(
    url: StrOrURL,
    local: Optional[PathLike] = None,
    buffer: int = 32768,
    echo_progress: Optional[Callable[..., Awaitable]] = None,
    **get_kw,
):
    """async-download a url to a the given path.

    :param local: where to download
    :param echo_progress: async function to receive downloaded size and total size as int.

    :return: size
    """
    url = url if isinstance(url, URL) else URL(url)
    local = Path(local or url.name)
    local.parent.mkdir(parents=True, exist_ok=True)

    if local.is_dir():
        local = local / url.name
        log.info(f"Changing local path from {local.parent.as_posix()} to {local.as_posix()}")
        if local.is_dir():
            raise FileExistsError(local)

    if local.exists():
        log.warning(f"{local.as_posix()} exists. Overwrite.")

    acc = 0
    async with aiohttp.ClientSession() as sess, aiofiles.open(local, "wb") as f, sess.get(
        url, **get_kw
    ) as r:
        size = int(r.headers.get("Content-Length", -1))
        it = r.content.iter_chunked(buffer)

        log.info(f"Starting download task {url} -> {local}")
        log.debug(f"File size: {size}")

        async for c in it:
            if not c:
                continue
            if echo_progress:
                ad, _ = await asyncio.gather(f.write(c), echo_progress(completed=acc, total=size))
                acc += ad
            else:
                acc += await f.write(c)

    if size > 0 and acc != size:
        log.error(f"Content-Length is {size} but {acc} downloaded")
    return acc
