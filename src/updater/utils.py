import re
from functools import partial
from typing import Callable, Union

from packaging.specifiers import SpecifierSet
from packaging.version import InvalidVersion

from .type import Asset, Release, Updater
from .version import parse


def pattern_filter_on_release(
    updater: Updater,
    pattern: Union[str, re.Pattern],
    ref: Callable[[Release], str],
    **kwds,
):
    if isinstance(pattern, str):
        pattern = re.compile(pattern)

    pred = lambda r: pattern.fullmatch(ref(r)) is not None
    return updater.filter_on_release(pred, **kwds)


def pattern_filter_on_asset(
    updater: Updater,
    pattern: Union[str, re.Pattern],
    ref: Callable[[Asset], str],
    **kwds,
):
    if isinstance(pattern, str):
        pattern = re.compile(pattern)

    pred = lambda a: pattern.fullmatch(ref(a)) is not None
    return updater.filter_on_asset(pred, **kwds)


def version_filter(
    updater: Updater,
    spec: Union[str, SpecifierSet],
    try_title=True,
    skip_legacy=True,
    **kwds,
):
    if isinstance(spec, str):
        spec = SpecifierSet(spec, prereleases=True)

    def pred(r: Release):
        if try_title and r.title:
            try:
                return parse(r.title) in spec
            except InvalidVersion:
                pass

        if r.tag:
            try:
                return parse(r.tag) in spec
            except InvalidVersion:
                if skip_legacy:
                    return False
                raise

        return False

    return updater.filter_on_release(pred, **kwds)


release_tag_filter = partial(pattern_filter_on_release, ref=lambda a: a.tag)
release_name_filter = partial(pattern_filter_on_release, ref=lambda a: a.title)
asset_name_filter = partial(pattern_filter_on_asset, ref=lambda a: a.name)


async def get_latest_asset(updater: Updater, pattern: Union[re.Pattern, str], **kwds):
    if not isinstance(pattern, re.Pattern):
        pattern = re.compile(pattern)
    r = asset_name_filter(updater, pattern, **kwds)
    try:
        return await r.__anext__()
    except StopAsyncIteration:
        raise FileNotFoundError(pattern)
