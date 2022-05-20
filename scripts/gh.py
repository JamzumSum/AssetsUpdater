import argparse
import asyncio
from pathlib import Path
from typing import Optional

from aiohttp import ClientSession as Session
from rich import print
from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from scripts.style.prompt import IndexPrompt
from updater.download import download as adownload
from updater.github import GhUpdater
from updater.type import Asset
from updater.utils import version_filter

console = Console()


def lookup(args: argparse.Namespace) -> Optional[Asset]:
    async def inner():
        async with Session() as sess:
            up = GhUpdater(sess, args.user, args.repo, args.num)
            up.proxy = args.proxy = args.proxy or up.proxy
            if args.spec:
                it = version_filter(up, args.spec, args.num, args.pre)
            else:
                it = up.all_iter(args.num, args.pre)

            l = [i async for i in it]
            i = IndexPrompt.ask(l, "Select a release", default=0, console=console)

            console.clear()
            print("Selected:", {"tag": l[i].tag, "title": l[i].title, "pre": l[i].pre})

            l = l[i].assets()
            if not l:
                print("No assets found.")
                return

            i = IndexPrompt.ask(l, "Select an asset")

            console.clear()
            a = l[i]
            print("Selected:", {"release_tag": a.from_tag, "name": a.name, "url": a.download_url})
            return a

    return asyncio.run(inner())


def download(args: argparse.Namespace):
    a = lookup(args)
    if a is None:
        return

    async def rich_adapter(completed: int, total: int):
        pg.update(tid, completed=completed, total=total)

    with Progress(
        TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeRemainingColumn(),
    ) as pg:
        tid = pg.add_task("Download", total=None, filename=a.name)
        coro = adownload(a.download_url, args.dest, proxy=args.proxy, echo_progress=rich_adapter)
        asyncio.run(coro)

    console.clear()


if __name__ == "__main__":
    psr = argparse.ArgumentParser()
    psrs = psr.add_subparsers()
    spsr = psrs.add_parser("download")

    spsr.set_defaults(run=download)
    spsr.add_argument("user", help="GiHub user name")
    spsr.add_argument("repo", help="GitHub repo name")
    spsr.add_argument("--num", "-n", type=int, default=10)
    spsr.add_argument(
        "--proxy", "-p", help="HTTPS_PROXY is read automatically, or you may override it here."
    )
    spsr.add_argument("--no-pre", action="store_false", dest="pre")
    spsr.add_argument(
        "--spec",
        "-s",
        default="",
        help="Requirement Specifiers "
        "https://pip.pypa.io/en/stable/reference/requirement-specifiers/",
    )
    spsr.add_argument("--dest", "-d", type=Path, help="destination")
    spsr.add_argument("--latest", action="store_false")

    spsr = psrs.add_parser("lookup")
    spsr.set_defaults(run=lookup)
    spsr.add_argument("user", help="GiHub user name")
    spsr.add_argument("repo", help="GitHub repo name")
    spsr.add_argument("--num", "-n", type=int, default=10)
    spsr.add_argument(
        "--proxy", "-p", help="HTTPS_PROXY is read automatically, or you may override it here."
    )
    spsr.add_argument("--no-pre", action="store_false", dest="pre")
    spsr.add_argument(
        "--spec",
        "-s",
        default="",
        help="Requirement Specifiers "
        "https://pip.pypa.io/en/stable/reference/requirement-specifiers/",
    )

    args = psr.parse_args()
    args.run(args)
