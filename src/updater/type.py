from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncGenerator, Callable, List, Optional

Pred = Callable[["Release"], bool]


@dataclass(frozen=True)
class Asset:
    from_release: "Release"
    name: str
    download_url: str

    def __repr__(self) -> str:
        return self.name

    @property
    def from_tag(self) -> str:
        return self.from_release.tag


class Release(ABC):
    @property
    @abstractmethod
    def tag(self) -> str:
        return ""

    @property
    @abstractmethod
    def title(self) -> str:
        return ""

    @abstractmethod
    def assets(self) -> List[Asset]:
        return []

    @property
    @abstractmethod
    def pre(self) -> bool:
        return False

    @property
    @abstractmethod
    def draft(self) -> bool:
        return False

    @property
    @abstractmethod
    def body(self) -> str:
        return ""

    def has_asset(self, name: str):
        for i in self.assets():
            if i.name == name:
                return True
        return False

    def __repr__(self) -> str:
        tag = f"<{self.tag}> " if self.tag else ""
        return tag + self.title


class Updater(ABC):
    @abstractmethod
    async def latest(self, pre: bool = False) -> Optional[Release]:
        return

    @abstractmethod
    def all_iter(
        self, num: Optional[int], pre: bool = False, start: int = 0, **kwds
    ) -> AsyncGenerator[Release, None]:
        pass

    async def all(self, num: Optional[int], pre: bool = False) -> List[Release]:
        return [i async for i in self.all_iter(num, pre)]

    async def filter(self, pred: Pred, pre: bool = False, start: int = 0, **kwds):
        async for i in self.all_iter(None, pre, start, **kwds):
            if pred(i):
                yield i
