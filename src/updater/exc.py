from typing import Optional


class ReleaseNotFound(RuntimeError):
    def __init__(self, index: str, msg: Optional[str]) -> None:
        super().__init__(index, msg)

    def __str__(self) -> str:
        msg = self.args[1] or ""
        if msg:
            return msg + f" ({self.args[0]} not found)"
        return f"{self.args[0]} not found"
