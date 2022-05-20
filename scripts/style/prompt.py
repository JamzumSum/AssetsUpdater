from typing import Any, Callable, List, Optional, TextIO, Type, TypeVar, Union, overload

from rich.console import Console
from rich.prompt import InvalidResponse, PromptBase
from rich.text import Text, TextType

IndexType = TypeVar("IndexType")


class IndexPrompt(PromptBase[IndexType]):
    response_type: Union[Type[IndexType], Callable[[str], IndexType]]
    choices: List
    indexes: Optional[List[str]] = None
    sep = "\n"
    end = "\n"

    def __init__(
        self,
        prompt: TextType = "",
        *,
        console: Optional[Console] = None,
        password: bool = False,
        choices: List,
        indexes: Optional[List[IndexType]] = None,
        show_default: bool = True,
        show_choices: bool = True,
    ) -> None:
        super().__init__(
            prompt,
            console=console,
            password=password,
            choices=choices,
            show_default=show_default,
            show_choices=show_choices,
        )
        if indexes:
            assert len(indexes) == len(choices)
            self.indexes = [str(i) for i in indexes]
            if not hasattr(self.__class__, "response_type") and not hasattr(self, "response_type"):
                self.response_type = type(indexes[0])
        else:
            self.response_type = int

    def process_response(self, value: str) -> IndexType:
        value = value.strip()
        try:
            return_value = self.response_type(value)
        except ValueError:
            raise InvalidResponse(self.validate_error_message)

        if not self.check_choice(value):
            raise InvalidResponse(self.illegal_choice_message)

        return return_value

    def check_choice(self, value: str) -> bool:
        if self.indexes is None:
            return 0 <= int(value) < len(self.choices)
        return value.strip() in self.indexes

    def render_default(self, default: IndexType) -> Text:
        if self.indexes:
            i = self.indexes.index(str(default))
        else:
            assert isinstance(default, int)
            i = default
        return Text(f"({self.choices[i]})", "prompt.default")

    def make_prompt(self, default: IndexType) -> Text:
        prompt = self.prompt.copy()
        prompt.end = self.end
        if self.indexes:
            indexes = self.indexes
        else:
            indexes = range(len(self.choices))

        if self.show_choices and self.choices:
            choices = self.sep.join(f"{i}. {c}" for i, c in zip(indexes, self.choices))
            prompt.append(self.sep)
            prompt.append(choices, "prompt.choices")

        if default != ... and self.show_default:
            prompt.append(self.sep)
            _default = self.render_default(default)
            prompt.append(_default)

        prompt.append(self.prompt_suffix)

        return prompt

    @classmethod
    @overload
    def ask(
        cls,
        choices: List,
        prompt: TextType = "",
        *,
        console: Optional[Console] = None,
        password: bool = False,
        show_default: bool = True,
        show_choices: bool = True,
        default: int = ...,
        stream: Optional[TextIO] = None,
    ) -> int:
        ...

    @classmethod
    @overload
    def ask(
        cls,
        choices: List,
        prompt: TextType = "",
        *,
        console: Optional[Console] = None,
        password: bool = False,
        indexes: List[IndexType],
        show_default: bool = True,
        show_choices: bool = True,
        default: IndexType = ...,
        stream: Optional[TextIO] = None,
    ) -> IndexType:
        ...

    @classmethod
    def ask(
        cls,
        choices: List,
        prompt: TextType = "",
        *,
        console: Optional[Console] = None,
        password: bool = False,
        indexes: Optional[List[IndexType]] = None,
        show_default: bool = True,
        show_choices: bool = True,
        default: IndexType = ...,
        stream: Optional[TextIO] = None,
    ) -> Any:
        _prompt = cls(
            prompt,
            console=console,
            password=password,
            choices=choices,
            indexes=indexes,
            show_default=show_default,
            show_choices=show_choices,
        )
        return _prompt(default=default, stream=stream)
