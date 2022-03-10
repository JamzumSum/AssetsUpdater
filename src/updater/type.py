from abc import ABC
from abc import abstractmethod
from abc import abstractproperty
from dataclasses import dataclass
from typing import Callable, Generator, List, Optional

Url = str
Pred = Callable[["Release"], bool]


@dataclass(frozen=True)
class Asset:
    from_tag: str
    name: str
    download_url: str

    def __repr__(self) -> str:
        return self.name


class Release(ABC):
    @abstractproperty
    def tag(self) -> str:
        return ""

    @abstractproperty
    def title(self) -> str:
        return ""

    @abstractmethod
    def assets(self) -> List[Asset]:
        return []

    @abstractproperty
    def pre(self) -> bool:
        return False

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
    def latest(self, pre: bool = False) -> Optional[Release]:
        return

    @abstractmethod
    def all_iter(self, num: Optional[int], pre: bool = False) -> Generator[Release, None, None]:
        pass

    def all(self, num: Optional[int], pre: bool = False) -> List[Release]:
        return list(self.all_iter(num, pre))

    def filter(self, pred: Pred, pre: bool = False):
        """Hint: Use `itertools.islice` to limit number"""
        return filter(pred, self.all(None, pre))
