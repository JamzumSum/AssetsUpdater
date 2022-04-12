import itertools
import re
from typing import Any, AsyncGenerator, Callable, Generator, Optional, Union

from packaging.specifiers import SpecifierSet
from packaging.version import InvalidVersion
from packaging.version import Version

from .type import Release
from .type import Updater
from .version import parse

__all__ = ["get_latest_asset", "tag_filter", "name_filter"]


async def get_latest_asset(updater: Updater, name: str, pre: bool = False):
    r = updater.filter(lambda r: r.has_asset(name), pre)
    try:
        r = await r.__anext__()
    except StopAsyncIteration:
        raise FileNotFoundError("No release found")

    f = next(filter(lambda i: i.name == name, r.assets()), None)
    if not f:
        raise FileNotFoundError(name)
    return f


async def _pattern_filter(
    updater: Updater,
    pattern: Union[str, re.Pattern],
    ref: Callable[[Release], str],
    num: Optional[int],
    pre=False,
) -> AsyncGenerator[Release, None]:
    if isinstance(pattern, str):
        pattern = re.compile(pattern)
    pred = lambda r: pattern.match(ref(r)) is not None

    i = 0
    async for r in updater.filter(pred, pre=pre):
        i += 1
        if num is None or i < num:
            yield r
        else:
            break


async def version_filter(
    updater: Updater,
    spec: Union[str, SpecifierSet],
    num: Optional[int],
    pre=False,
    try_title=True,
    skip_legacy=True,
):
    if isinstance(spec, str):
        spec = SpecifierSet(spec)

    def pred(r: Release):
        if try_title and r.title:
            v = parse(r.title)
            if isinstance(v, Version):
                return v in spec

        if r.tag:
            v = parse(r.tag)
            if isinstance(v, Version):
                return v in spec
        if not skip_legacy:
            raise InvalidVersion(r.tag)

    i = 0
    async for r in updater.all_iter(None, pre=pre):
        if pred(r):
            i += 1
            if num is None or i < num:
                yield r


def tag_filter(updater: Updater, pattern: Union[str, re.Pattern], num, pre=False):
    return _pattern_filter(updater, pattern, lambda a: a.tag, num, pre)


def name_filter(updater: Updater, pattern: Union[str, re.Pattern], num, pre=False):
    return _pattern_filter(updater, pattern, lambda a: a.title, num, pre)
