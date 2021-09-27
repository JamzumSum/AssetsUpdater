from dataclasses import dataclass
from typing import Optional, Union

import requests
from requests.exceptions import HTTPError

from updater.type import Asset, Release, Updater, Url

PROXY = None
RELEASE_LIMIT = 65536


@dataclass(frozen=True)
class Repo:
    user: str
    repo: str


def register_proxy(proxy: dict):
    global PROXY
    PROXY = proxy.copy()
    return proxy


class GhRelease(Release):
    def __init__(self, raw: dict) -> None:
        self.raw = raw

    @property
    def pre(self) -> bool:
        return self.raw['prerelease']

    def assets(self):
        return [Asset(i['name'], i['browser_download_url']) for i in self.raw['assets']]

    @property
    def title(self) -> str:
        return self.raw['name']

    @property
    def tag(self) -> Optional[str]:
        return self.raw.get('tag_name', None)


class GhUpdater(Updater):
    def __init__(self, repo: Union[Repo, Url]) -> None:
        super().__init__()
        self.url = repo if isinstance(
            repo, Url
        ) else f"https://api.github.com/repos/{repo.user}/{repo.repo}/releases"

    def all_iter(self, num=None, pre=False):
        header = {
            'accept': 'application/vnd.github.v3+json',
        }
        if num is None: num = RELEASE_LIMIT
        for i in range(0, num, 100):
            query = {
                'per_page': min(100, num - i),
                'page': int(i // 100) + 1,
            }
            r = requests.get(self.url, params=query, headers=header, proxies=PROXY)
            if r.status_code != 200: raise HTTPError(response=r)

            r = r.json()
            wo_draft = (GhRelease(i) for i in r if not i['draft'])
            if pre: yield from wo_draft
            yield from filter(lambda i: not i.pre, wo_draft)

            if len(r) < query['per_page']: break

    def latest(self, pre=False) -> Optional[Release]:
        if pre: return self.all(1, pre=True)[0]
        header = {
            'accept': 'application/vnd.github.v3+json',
        }
        r = requests.get(self.url + '/latest', headers=header, proxies=PROXY)
        if r.status_code != 200: raise HTTPError(response=r)
        if not (r := r.json()): return
        return GhRelease(r)
