# For typehinting Deprecated-params's cython speedup module.
import sys
from typing import (Any, Callable, Iterable, Mapping, Sequence, TypeVar,
                    overload)

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec

# Typehinting this only... 
# DO NOT ATTEMPT TO IMPORT FROM _helpers_c FOR THE LOVE OF PETE
_T = TypeVar("_T")
_P = ParamSpec("_P")

class _KeywordsBaseException(Exception):
    def __init__(self, keywords: set[str], *args: Any) -> None: ...
    @property
    def keywords(self) -> frozenset[str]: ...
    @keywords.setter
    def keywords(self, _: frozenset[str]) -> None: ...

class MissingKeywordsError(_KeywordsBaseException):
    def __init__(self, keywords: set[str], *args: Any) -> None: ...

class InvalidParametersError(_KeywordsBaseException):
    def __init__(self, keywords: set[str], *args: Any) -> None: ...

class deprecated_params:
    def __init__(self, params: Sequence[str] | Iterable[str] | str, message: str | Mapping[str, str] = 'is deprecated', /, *, default_message: str | None = None, category: type[Warning] | None = ..., stacklevel: int = 3, display_kw: bool = True, removed_in: str | Sequence[int] | Mapping[str, str | Sequence[int]] | None = None) -> None: ...
    @overload
    def __call__(self, arg: type[_T]) -> type[_T]: ...
    @overload
    def __call__(self, arg: Callable[_P, _T]) -> Callable[_P, _T]: ...
