from abc import ABC, abstractmethod, abstractproperty
from dataclasses import dataclass
from typing import Generator, List, Optional, Callable

Url = str


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
        return ''

    @abstractproperty
    def title(self) -> str:
        return ''

    @abstractmethod
    def assets(self) -> List[Asset]:
        return []

    @abstractproperty
    def pre(self) -> bool:
        return False

    def has_asset(self, name):
        for i in self.assets():
            if i.name == name: return True
        return False

    def __repr__(self) -> str:
        tag = f"<{self.tag}> " if self.tag else ''
        return tag + self.title


Pred = Callable[[Release], bool]


class Updater(ABC):
    @abstractmethod
    def latest(self, pre=False) -> Optional[Release]:
        return

    @abstractmethod
    def all_iter(self, num, pre=False) -> Generator[Release, None, None]:
        yield

    def all(self, num, pre=False) -> List[Release]:
        return list(self.all_iter(num, pre))

    def filter(self, pred: Pred, pre=False):
        """Hint: Use `itertools.islice` to limit number
        """
        return filter(pred, self.all(None, pre))
