import asyncio
import logging
from os import PathLike
from pathlib import Path
from typing import Awaitable, Callable, Optional

import aiofiles
from httpx import URL, AsyncClient
from httpx._types import ProxiesTypes, URLTypes

log = logging.getLogger(__name__)

__all__ = ["download"]


async def download(
    url: URLTypes,
    local: Optional[PathLike] = None,
    buffer: int = 32768,
    echo_progress: Optional[Callable[..., Awaitable]] = None,
    proxy: ProxiesTypes = ...,
):
    """async-download a url to a the given path.

    :param local: where to download
    :param echo_progress: async function to receive downloaded size and total size as int.

    :return: size
    """
    url = url if isinstance(url, URL) else URL(url)
    remote_name = Path(url.path).name
    local = Path(local or remote_name)
    local.parent.mkdir(parents=True, exist_ok=True)

    if local.is_dir():
        local = local / remote_name
        log.info(f"Changing local path from {local.parent.as_posix()} to {local.as_posix()}")
        if local.is_dir():
            raise FileExistsError(local)

    if local.exists():
        log.warning(f"{local.as_posix()} exists. Overwrite.")

    client_dict = {}
    if proxy != ...:
        client_dict["proxies"] = proxy

    acc = 0
    async with AsyncClient(**client_dict) as client, aiofiles.open(local, "wb") as f:
        r = await client.get(url, follow_redirects=True)
        r.raise_for_status()

        size = int(r.headers.get("Content-Length", -1))
        it = r.aiter_bytes(chunk_size=buffer)

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
