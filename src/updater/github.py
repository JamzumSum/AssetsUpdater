from typing import Optional

from aiohttp import ClientSession as Session
from aiohttp.typedefs import StrOrURL
from yarl import URL

from updater.type import Asset, Release, Updater

from .exc import ReleaseNotFound

RELEASE_LIMIT = 65536


class GhRelease(Release):
    def __init__(self, raw: dict) -> None:
        self.raw = raw

    @property
    def pre(self) -> bool:
        return self.raw["prerelease"]

    def assets(self):
        return [Asset(self.tag, i["name"], i["browser_download_url"]) for i in self.raw["assets"]]

    @property
    def title(self) -> str:
        return self.raw["name"]

    @property
    def tag(self) -> str:
        return self.raw.get("tag_name", None)


class GhUpdater(Updater):
    from os import environ as env

    host = URL("https://api.github.com")
    proxy: Optional[StrOrURL] = env.get("HTTPS_PROXY") or env.get("https_proxy")

    def __init__(self, sess: Session, user: str, repo: str, pagesize: int = 100) -> None:
        super().__init__()
        self.usr = user
        self.repo = repo
        self.sess = sess
        self.sess.headers["accept"] = "application/vnd.github.v3+json"

        self.pagesize = pagesize

    @property
    def _api(self):
        return self.host / f"repos/{self.usr}/{self.repo}/releases"

    async def all_iter(
        self,
        num: Optional[int] = None,
        pre: bool = False,
        start: int = 0,
        pagesize: Optional[int] = None,
    ):
        num = num or RELEASE_LIMIT
        pagesize = pagesize or self.pagesize

        for i in range(start, start + num, pagesize):
            query = {
                "per_page": min(pagesize, num - i),
                "page": int(i / pagesize) + 1,
            }
            async with self.sess.get(self._api, params=query, proxy=self.proxy) as r:
                if not r.ok:
                    raise ReleaseNotFound(f"{self.usr}/{self.repo}", r.reason)
                r = await r.json()

            if isinstance(r, dict):
                raise ReleaseNotFound(f"{self.usr}/{self.repo}", r["message"])

            wo_draft = (GhRelease(i) for i in r if not i["draft"])
            yield_from = wo_draft
            if not pre:
                yield_from = filter(lambda i: not i.pre, wo_draft)
            for i in yield_from:
                yield i

            if len(r) < query["per_page"]:
                break

    async def latest(self, pre=False) -> Optional[Release]:
        if pre:
            return await self.all_iter(1, pre=True, pagesize=1).__anext__()
        async with self.sess.get(self._api / "latest", proxy=self.proxy) as r:
            if not r.ok:
                raise ReleaseNotFound(f"{self.usr}/{self.repo}", r.reason)
            r = await r.json()
        if not r:
            return
        return GhRelease(r)
