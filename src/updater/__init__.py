import itertools
import re
from typing import Any, Callable, Generator, Union

from .type import Release, Updater
from .download import *


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
    num,
    pre=False
) -> Generator[Release, Any, Any]:
    if isinstance(pattern, str):
        pattern = re.compile(pattern)
    pred = lambda r: (r := ref(r)) is not None and pattern.match(r)
    yield from itertools.islice(updater.filter(pred, pre=pre), num)


def tag_filter(updater: Updater, pattern: Union[str, re.Pattern], num, pre=False):
    return _pattern_filter(updater, pattern, lambda a: a.tag, num, pre)


def name_filter(updater: Updater, pattern: Union[str, re.Pattern], num, pre=False):
    return _pattern_filter(updater, pattern, lambda a: a.title, num, pre)


__all__ = [i.__name__ for i in [
    get_latest_asset,
    tag_filter,
    name_filter,
]]
