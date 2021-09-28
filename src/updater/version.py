from functools import wraps

from packaging.version import parse as _parse


@wraps(_parse)
def parse(version: str):
    if version.startswith('v'):
        version = version[1:]
    return _parse(version)
