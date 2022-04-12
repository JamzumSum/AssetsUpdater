from typing import Optional

from aiohttp import ClientError
from aiohttp import ClientSession as Session
from aiohttp.typedefs import StrOrURL
from yarl import URL

from updater.type import Asset
from updater.type import Release
from updater.type import Updater

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

    def __init__(self, sess: Session, user: str, repo: str) -> None:
        super().__init__()
        self.sess = sess
        self.sess.headers["accept"] = "application/vnd.github.v3+json"
        self._api = self.host / f"repos/{user}/{repo}/releases"

    async def all_iter(self, num=None, pre=False):
        num = num or RELEASE_LIMIT

        for i in range(0, num, 100):
            query = {
                "per_page": min(100, num - i),
                "page": int(i / 100) + 1,
            }
            async with self.sess.get(self._api, params=query, proxy=self.proxy) as r:
                r.raise_for_status()
                r = await r.json()

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
            return (await self.all(1, pre=True))[0]
        async with self.sess.get(self._api / "latest", proxy=self.proxy) as r:
            r.raise_for_status()
            r = await r.json()
        if not r:
            return
        return GhRelease(r)


async def demo(user: str, repo: str, *, proxy: Optional[str], spec: str = "", num: int = 10):
    from sys import stderr as STDERR

    from .utils import version_filter

    def choose(ls: list, prompt: str, default: int = 0):
        for i, r in enumerate(ls):
            print(f"{i}.", repr(r))
        c = ""
        try:
            c = input(f"{prompt} [{default}]: ") or default
            c = int(c)
            if not (0 <= c < len(ls)):
                print("wrong input range, exit", file=STDERR)
                return
            return c
        except KeyboardInterrupt:
            return
        except ValueError:
            print(f"wrong input: {c}, exit", file=STDERR)

    async with Session() as sess:
        up = GhUpdater(sess, user, repo)
        if proxy:
            up.proxy = proxy

        try:
            l = version_filter(up, spec, num)
        except ClientError as e:
            print(str(e), file=STDERR)
            print("You may set an proxy using '-p' or '--proxy'.")
            return

        l = [i async for i in l]

    c = choose(l, "Choose a release")
    if c is None:
        return

    print("#", l[c].title)
    l = l[c].assets()
    c = choose(l, "Choose an asset")
    if c is None:
        return

    from .download import download

    print(await download(l[c].download_url))


def main():
    import argparse
    import asyncio

    psr = argparse.ArgumentParser()
    psr.add_argument("user", help="GiHub user name")
    psr.add_argument("repo", help="GitHub repo name")
    psr.add_argument(
        "--proxy", "-p", help="HTTPS_PROXY is read automatically, or you may override it here."
    )
    psr.add_argument("--spec", "-s", default="", help="such as '>=1.0' or '~=1.11'")

    arg = psr.parse_args()
    coro = demo(arg.user, arg.repo, spec=arg.spec, proxy=arg.proxy)
    asyncio.run(coro)


if __name__ == "__main__":
    main()
