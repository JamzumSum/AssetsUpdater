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


def register_proxy(proxy: dict, auth: dict = None):
    global PROXY
    if auth is None:
        PROXY = proxy.copy()
        return proxy

    assert 'username' in auth
    assert 'password' in auth
    from urllib.parse import urlsplit
    PROXY = {}

    for k in proxy:
        p = urlsplit(proxy[k])
        assert p.hostname
        url = f"{p.scheme}://{auth['username']}:{auth['password']}@{p.hostname}"
        if p.port: url += f":{p.port}"
        PROXY[k] = url

    return PROXY


class GhRelease(Release):
    def __init__(self, raw: dict) -> None:
        self.raw = raw

    @property
    def pre(self) -> bool:
        return self.raw['prerelease']

    def assets(self):
        return [Asset(self.tag, i['name'], i['browser_download_url']) for i in self.raw['assets']]

    @property
    def title(self) -> str:
        return self.raw['name']

    @property
    def tag(self) -> str:
        return self.raw.get('tag_name', None)


class GhUpdater(Updater):
    def __init__(self, repo: Union[Repo, Url]) -> None:
        super().__init__()
        if isinstance(repo, Url):
            import re
            m = re.search(r'github.com/(?:repos/)?(\w+)/(\w+)', repo)
            if not m: raise ValueError("Cannot parse " + repo)
            repo = Repo(user=m.group(1), repo=m.group(2))

        if not isinstance(repo, Repo):
            raise TypeError(repo)

        self.url = f"https://api.github.com/repos/{repo.user}/{repo.repo}/releases"

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
