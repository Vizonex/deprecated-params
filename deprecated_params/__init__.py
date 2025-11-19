"""
Deprecated Params
-----------------

A Library dedicated for warning users about deprecated parameter
names and changes
"""

from __future__ import annotations

import inspect
import sys
import warnings
from functools import wraps
from types import MethodType
from typing import (
    Any,
    Callable,
    Iterable,
    Mapping,
    Sequence,
    TypeVar,
    overload,
    ParamSpec,
)

if sys.version_info[:2] < (3, 13):
    from typing_extensions import deprecated
else:
    from warnings import deprecated


__version__ = "0.3.0"
__license__ = "Apache 2.0 / MIT"
__author__ = "Vizonex"

_T = TypeVar("_T", covariant=True)
_P = ParamSpec("_P")

KEYWORD_ONLY = inspect.Parameter.KEYWORD_ONLY
VAR_KEYWORD = inspect.Parameter.VAR_KEYWORD


__all__ = (
    "MissingKeywordsError",
    "InvalidParametersError",
    "deprecated_params",
    "__author__",
    "__license__",
    "__version__",
)

# Word of Warning:
# All functions marked with underscores should be treated as do not use
# directly. If you want these parts of code, they are under an MIT License and you
# are allowed to copy and paste them freely as long as it's not apart of python's
# warnings.deprecated function which then you will need to license under an APACHE 2.0


class _KeywordsBaseException(Exception):
    __slots__ = "_keywords"

    def __init__(self, keywords: set[str], *args: Any) -> None:
        self._keywords = frozenset(keywords)
        super().__init__(*args)

    @property
    def keywords(self) -> frozenset[str]:
        """tells what keywords were bad"""
        return self._keywords

    @keywords.setter
    def keywords(self, _: frozenset[str]) -> None:
        """Throws ValueError because keywords is an
        immutable property that shouldn't be edited."""
        raise ValueError("keywords property is immutable")


class MissingKeywordsError(_KeywordsBaseException):
    """Raised when Missing a keyword for an argument"""

    def __init__(self, keywords: set[str], *args: Any) -> None:
        """Initializes missing keywords"""
        super().__init__(
            keywords,
            f"Missing Keyword arguments for: {list(keywords)!r}",
            *args,
        )


class InvalidParametersError(_KeywordsBaseException):
    """Raised when Parameters were positional arguments without defaults or keyword arguments"""

    def __init__(self, keywords: set[str], *args: Any) -> None:
        """initializes invalid keywords, deprecated parameters should not be positional arguments
        as that would defeat the purpose of deprecating a function's parameters."""
        super().__init__(
            keywords,
            f"Arguments :{list(keywords)!r} should not be positional",
            *args,
        )


def join_version_if_sequence(ver: str | Sequence[int]) -> str:
    return ".".join(map(str, ver)) if not isinstance(ver, str) else ver


def convert_removed_in_sequences(
    removed_in: Mapping[str, str | Sequence[int]],
) -> dict[str, str]:
    return {k: join_version_if_sequence(v) for k, v in removed_in.items()}


class deprecated_params:
    """
    A Wrapper inspired by python's wrapper deprecated from 3.13
    and is used to deprecate parameters.

    Since version 0.1.8 this wrapper also passes along an attribute
    called `__deprecated_params__` with a dictionary of all the
    preloaded deprecation warnings to each given parameter. Ides
    such as VSCode, Pycharm and more could theoretically utilize
    `__deprecated_params__` elsewhere help to assist users and developers
    while writing and editing code.
    """

    # __slots__ was an optimizations since subclassing deprecated_params should really be discouraged
    # if this is not your case scenario and you must subclass this object throw me an issue.

    __slots__ = (
        "_params",
        "_message",
        "_message_is_dict",
        "_display_kw",
        "_category",
        "_stacklevel",
        "_default_message",
        "_removed_in",
        "_warning_messages",
    )

    @deprecated("subclassing will not be allowed in version 0.4.0")
    def __init_subclass__(cls) -> None:
        pass

    def __init__(
        self,
        params: Sequence[str] | Iterable[str] | str,
        message: str | Mapping[str, str] = "is deprecated",
        /,
        *,
        # default_message should be utilized when a keyword isn't
        # given in message if messaged is defined as a dictionary.
        default_message: str | None = None,
        category: type[Warning] | None = DeprecationWarning,
        stacklevel: int = 1,
        display_kw: bool = True,
        # removed_in is inspired by the deprecation library
        removed_in: str
        | Sequence[int]
        | Mapping[str, str | Sequence[int]]
        | None = None,
    ) -> None:
        """
        Initializes deprecated parameters to pass along to different functions

        :param params: A Sequence of keyword parameters of single keyword parameter to deprecate and warn the removal of.
        :param message: A single message for to assign to each parameter to be deprecated otherwise
            you can deprecate multiple under different reasons::

                @deprecated_params(
                    ['mispel', 'x'],
                    message={
                        'mispel': 'mispel was deprecated due to misspelling the word',
                        'x':'you get the idea...'
                    }
                )
                def mispelled_func(misspelling = None, *, mispel:str, x:int): ...

        :param category: Used to warrant a custom warning category if required or needed to specify what
            Deprecation warning should appear.
        :param stacklevel: What level should this wanring appear at? Default: 1
        :param default_message: When a parameter doesn't have a warning message try using this message instead
        :param display_kw: Displays which parameter is deprecated in the warning message under `Parameter "%s" ...`
            followed by the rest of the message
        :param removed_in: Displays which version of your library's program will remove this keyword parameter in::

                @deprecated_params(
                    ['mispel', 'x'],
                    removed_in={
                        'mispel':'0.1.4',
                        'x':(0, 1, 3)
                    } # sequences of numbers are also allowed if preferred.
                )

                def mispelled_func(misspelling = None, *, mispel:str, x:int): ...

            you can also say that all parameters will be removed in one version::

                @deprecated_params(
                    ['mispel', 'x'],
                    removed_in='0.1.5' # or (0, 1, 5)
                )
                def mispelled_func(misspelling = None, *, mispel:str, x:int): ...


        """
        if not params:
            raise ValueError(f"params should not be empty got {params!r}")
        if not isinstance(message, (str, dict, Mapping)):
            raise TypeError(
                f"Expected an object of type str or dict or Mappable type for 'message', not {type(message).__name__!r}"
            )

        self._params = (
            set(params) if not isinstance(params, str) else set([params])
        )

        self._message = message or "is deprecated"
        self._message_is_dict = isinstance(message, (Mapping, dict))
        self._display_kw = display_kw
        self._category = category
        self._stacklevel = stacklevel
        self._default_message = default_message or "do not use"

        if removed_in:
            if isinstance(removed_in, (dict, Mapping)):
                # Some people might be more comfortable giving versions in tuples or lists.
                self._removed_in = convert_removed_in_sequences(removed_in)
            else:
                # single removed version meaning that all parameters will be removed in this version
                ver = join_version_if_sequence(removed_in)
                self._removed_in = {k: ver for k in params}
        else:
            self._removed_in = {}

        # Preloaded previews of all warning messages new in deprecated-params 0.1.8 for extra speed
        # upon loading the message
        self._warning_messages: dict[str, str] = {
            p: self.__write_warning(p) for p in self._params
        }

    def __check_with_missing(
        self,
        fn: Callable[..., Any],
        missing: set[str] | None = None,
        invalid_params: set[str] | None = None,
        skip_missing: bool | None = None,
        allow_miss: bool = False,
    ) -> tuple[set[str], set[str], bool]:
        sig = inspect.signature(fn)

        missing = missing if missing is not None else set(self._params)
        invalid_params = set() if invalid_params is None else invalid_params

        skip_missing = (
            any([p.kind == VAR_KEYWORD for p in sig.parameters.values()])
            if skip_missing is None
            else skip_missing
        )

        for m in self._params:
            if not allow_miss:
                p = sig.parameters[m]
            else:
                p = sig.parameters.get(m)  # type: ignore
                if p is None:
                    continue

            # Check if were keyword only or aren't carrying a default param
            if p.kind != KEYWORD_ONLY:
                # Anything this isn't a keyword should be considered as deprecated
                # as were still technically using it.
                invalid_params.add(p.name)

            if not skip_missing:
                missing.remove(p.name)

        return missing, invalid_params, skip_missing

    def __check_for_missing_kwds(
        self,
        fn: Callable[..., Any],
        missing: set[str] | None = None,
        invalid_params: set[str] | None = None,
        skip_missing: bool | None = None,
        allow_miss: bool = False,
    ) -> None:
        # copy sequence to check for missing parameter names
        missing, invalid_params, skip_missing = self.__check_with_missing(
            fn, missing, invalid_params, skip_missing, allow_miss
        )

        if invalid_params:
            raise InvalidParametersError(invalid_params)

        if missing and not skip_missing:
            raise MissingKeywordsError(missing)

    def __write_warning(self, kw_name: str) -> str:
        msg = ""
        if self._display_kw:
            msg += 'Parameter "%s" ' % kw_name

        if self._message_is_dict:
            msg += self._message.get(kw_name, self._default_message)  # type: ignore
        else:
            msg += self._message  # type: ignore

        if self._removed_in:
            if kw_removed_in := self._removed_in.get(kw_name):
                msg += " [Removed In: "
                msg += kw_removed_in
                msg += "]"

        return msg

    def __warn(self, kw_name: str, source: Any) -> None:
        warnings.warn(
            self._warning_messages[kw_name],
            self._category,
            stacklevel=self._stacklevel + 1,
            source=source,
        )

    @overload
    def __call__(self, arg: type[_T]) -> type[_T]: ...

    @overload
    def __call__(self, arg: Callable[_P, _T]) -> Callable[_P, _T]: ...

    # Mirrors python's deprecated wrapper with a few changes
    # Since 0.1.8 a new attribute is added called __deprecated_params__
    # based off and inspired by python's __deprecated__ dunder value.

    def __call__(
        self, arg: type[_T] | Callable[_P, _T]
    ) -> type[_T] | Callable[_P, _T]:
        def check_kw_arguments(kw: dict[str, Any]) -> None:
            for k in self._params.intersection(kw.keys()):
                self.__warn(k, arg)

        if isinstance(arg, type):
            # NOTE: Combining init and new together is done to
            # solve deprecation of both new_args and init_args

            missing, invalid_params, skip_missing = self.__check_with_missing(
                arg, allow_miss=True
            )

            original_new: Callable[..., type[_T]] = arg.__new__
            self.__check_for_missing_kwds(
                original_new,
                missing,
                invalid_params,
                skip_missing,
                allow_miss=True,
            )

            @wraps(original_new)
            def __new__(
                cls: type[_T], *args: _P.args, **kwargs: _P.kwargs
            ) -> type[_T]:
                check_kw_arguments(kwargs)
                if original_new is not object.__new__:
                    return original_new(cls, *args, **kwargs)
                # Python Comment: Mirrors a similar check in object.__new__.
                elif cls.__init__ is object.__init__ and (args or kwargs):
                    raise TypeError(f"{cls.__name__}() takes no arguments")
                else:
                    return original_new(cls)

            arg.__new__ = staticmethod(__new__)  # type: ignore
            arg.__new__.__deprecated_params__ = self._warning_messages.copy()  # type: ignore

            original_init_subclass = arg.__init_subclass__
            # Python Comment: We need slightly different behavior if __init_subclass__
            # is a bound method (likely if it was implemented in Python)
            if isinstance(original_init_subclass, MethodType):
                self.__check_for_missing_kwds(
                    original_init_subclass,
                    missing,
                    invalid_params,
                    skip_missing,
                    allow_miss=True,
                )
                original_init_subclass = original_init_subclass.__func__

                @wraps(original_init_subclass)
                def __init_subclass__(
                    *args: _P.args, **kwargs: _P.kwargs
                ) -> Any:
                    check_kw_arguments(kwargs)
                    return original_init_subclass(*args, **kwargs)

                arg.__init_subclass__ = classmethod(__init_subclass__)  # type: ignore
                arg.__init_subclass__.__deprecated_params__ = (  # type: ignore[attr-defined]
                    self._warning_messages.copy()
                )

            # Python Comment: Or otherwise, which likely means it's a builtin such as
            # object's implementation of __init_subclass__.
            else:

                @wraps(original_init_subclass)
                def __init_subclass__(
                    *args: _P.args, **kwargs: _P.kwargs
                ) -> None:
                    check_kw_arguments(kwargs)
                    return original_init_subclass(*args, **kwargs)

                arg.__init_subclass__ = __init_subclass__  # type: ignore
                arg.__init_subclass__.__deprecated_params__ = (  # type: ignore[attr-defined]
                    self._warning_messages.copy()
                )
            return arg

        elif callable(arg):
            # Check for missing function arguments
            self.__check_for_missing_kwds(arg)

            @wraps(arg)
            def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
                check_kw_arguments(kwargs)
                return arg(*args, **kwargs)

            if sys.version_info >= (3, 12):
                if inspect.iscoroutinefunction(arg):
                    wrapper = inspect.markcoroutinefunction(wrapper)

            # Wrapper now contains a shadow copy of deprecated parameters
            wrapper.__deprecated_params__ = self._warning_messages.copy()  # type: ignore
            return wrapper

        else:
            raise TypeError(
                "@deprecated_params decorator with non-None category must be applied to "
                f"a class or callable, not {arg!r}"
            )
