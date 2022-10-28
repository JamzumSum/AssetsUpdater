import asyncio
import logging
from functools import wraps
from os import PathLike
from pathlib import Path
from typing import Awaitable, Callable, Optional

import aiofiles
from httpx import URL, AsyncClient
from httpx._types import ProxiesTypes, URLTypes

log = logging.getLogger(__name__)

__all__ = ["download"]


def _guard(func: Callable):
    warned = False

    @wraps(func)
    async def wrapper(*args, **kwds):
        try:
            return await func(*args, **kwds)
        except:
            nonlocal warned
            if not warned:
                log.error("Error caught by guard.", exc_info=True)
                warned = True

    return wrapper


async def download(
    url: URLTypes,
    local: Optional[PathLike] = None,
    buffer: int = 32768,
    echo_progress: Optional[Callable[..., Awaitable]] = None,
    *,
    client: Optional[AsyncClient] = None,
    proxy: Optional[ProxiesTypes] = None,
) -> int:
    """async-download a url to a the given path.

    :param local: where to download
    :param buffer: transfer buffer
    :param echo_progress: async function to receive downloaded size and total size as int.
    :param client: use this client, otherwise we will create one and close it on return.
    :param proxy: download proxy.
    :return: size

    .. warning:: actual proxy = client.proxy | param.proxy

    .. versionchanged:: 1.4.2

        added `client`; `proxy` is set as a keyword-only parameter.
    """
    if client is None:
        async with AsyncClient(proxies=proxy) as client:
            return await download(url, local, buffer, echo_progress, client=client, proxy=proxy)

    url = url if isinstance(url, URL) else URL(url)
    remote_name = Path(url.path).name
    local = Path(local or remote_name)
    local.parent.mkdir(parents=True, exist_ok=True)

    if local.is_dir():
        # if local not exist or is a directory
        local = local / remote_name
        log.info(f"Changing local path from {local.parent.as_posix()} to {local.as_posix()}")
        if local.is_dir():
            raise FileExistsError(local)

    if local.exists():
        log.warning(f"{local.as_posix()} exists. Overwrite.")

    if echo_progress:
        echo_progress = _guard(echo_progress)

    acc = 0
    async with aiofiles.open(local, "wb") as f:
        async with client.stream("GET", url, follow_redirects=True) as r:
            r.raise_for_status()

            size = int(r.headers.get("Content-Length", -1))

            log.info(f"Starting download task {url} -> {local}")
            log.debug(f"File size: {size}")

            async for c in r.aiter_bytes(chunk_size=buffer):
                if not c:
                    continue
                if echo_progress:
                    ad, _ = await asyncio.gather(
                        f.write(c), echo_progress(completed=acc, total=size)
                    )
                    acc += ad
                else:
                    acc += await f.write(c)

    if size > 0 and acc != size:
        log.error(f"Content-Length is {size} but {acc} downloaded")
    return acc
