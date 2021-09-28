import itertools
import re
from typing import Any, Callable, Generator, Optional, Union

from packaging.version import InvalidVersion, Version

from .type import Release, Updater
from .version import parse


def get_latest_asset(updater: Updater, name: str, pre=False):
    r = updater.filter(lambda r: r.has_asset(name), pre)
    r = next(r, None)
    if not r: raise FileNotFoundError('No release found')

    f = next(filter(lambda i: i.name == name, r.assets()), None)
    if not f: raise FileNotFoundError(name)
    return f


def _pattern_filter(
    updater: Updater,
    pattern: Union[str, re.Pattern],
    ref: Callable[[Release], str],
    num: Optional[int],
    pre=False
) -> Generator[Release, Any, Any]:
    if isinstance(pattern, str):
        pattern = re.compile(pattern)
    pred = lambda r: (r := ref(r)) is not None and pattern.match(r)
    yield from itertools.islice(updater.filter(pred, pre=pre), num)


def version_filter(
    updater: Updater,
    version: Union[str, Version],
    num: Optional[int],
    pre=False,
    try_title=True,
    skip_legacy=True
):
    if isinstance(version, str):
        version = parse(version)

    def pred(r: Release):
        if try_title and r.title and isinstance((v := parse(r.title)), Version):
            return v > version
        else:
            if r.tag and isinstance((v := parse(r.tag), Version)):
                return v > version
            elif not skip_legacy:
                raise InvalidVersion(r.tag)

    took = itertools.takewhile(pred, updater.all_iter(None, pre=pre))
    yield from itertools.islice(took, num)


def tag_filter(updater: Updater, pattern: Union[str, re.Pattern], num, pre=False):
    return _pattern_filter(updater, pattern, lambda a: a.tag, num, pre)


def name_filter(updater: Updater, pattern: Union[str, re.Pattern], num, pre=False):
    return _pattern_filter(updater, pattern, lambda a: a.title, num, pre)


# package meta

__all__ = [i.__name__ for i in [
    get_latest_asset,
    tag_filter,
    name_filter,
]]

