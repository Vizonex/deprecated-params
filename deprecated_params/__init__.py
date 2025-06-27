"""
Deprecated Params
-----------------

A Library dedicated for warning users about deprecated paramter
names and changes
"""

from __future__ import annotations

import inspect
import sys
import warnings
from functools import wraps
import inspect
from types import MethodType
from typing import Callable, Sequence, TypeVar, Mapping, overload

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec


__version__ = "0.1.3"
__license__ = "Appache 2.0 / MIT"


_T = TypeVar("_T", covariant=True)
_P = ParamSpec("_P")

KEYWORD_ONLY = inspect.Parameter.KEYWORD_ONLY
VAR_KEYWORD = inspect.Parameter.VAR_KEYWORD


__all__ = (
    "MissingKeywordsError",
    "InvalidParametersError",
    "deprecated_params",
)


class _KeywordsBaseException(Exception):
    def __init__(self, keywords: set[str], *args):
        self._keywords = keywords
        super().__init__(*args)

    @property
    def keywords(self):
        return self._keywords

    @keywords.setter
    def keywords(self, kw):
        raise ValueError("keywords property is immutable")


class MissingKeywordsError(_KeywordsBaseException):
    """Missing keyword for argument"""

    def __init__(self, keywords: set[str], *args):
        super().__init__(
            keywords, f"Missing Keyword arguments for: {list(keywords)!r}", *args
        )


class InvalidParametersError(_KeywordsBaseException):
    """Parameters were positonal arguments without defaults or keyword arguments"""

    def __init__(self, keywords: set[str], *args):
        super().__init__(
            keywords,
            f"Arguments :{list(keywords)!r} should not be positional",
            *args,
        )


class deprecated_params:
    """
    A Wrapper inspired by python's wrapper deprecated from 3.13
    and is used to deprecate parameters
    """

    def __init__(
        self,
        params: Sequence[str],
        message: str | Mapping[str, str] = "is deprecated",
        /,
        *,
        # default_message should be utilized when a keyword isn't
        # given in message if messaged is defined as a dictionary.
        default_message: str | None = None,
        category: type[Warning] | None = DeprecationWarning,
        stacklevel: int = 3,
        display_kw: bool = True,
    ):
        if not isinstance(message, (str, dict, Mapping)):
            raise TypeError(
                f"Expected an object of type str or dict or Mappable type for 'message', not {type(message).__name__!r}"
            )

        self.params = set(params)
        self.message = message or "is deprecated"
        self.message_is_dict = isinstance(message, (Mapping, dict))
        self.display_kw = display_kw
        self.category = category
        self.stacklevel = stacklevel
        self.default_message = default_message or "do not use"

    def __check_with_missing(
        self,
        fn,
        missing: set[str] | None = None,
        invalid_params: set[str] | None = None,
        skip_missing: bool | None = None,
        allow_miss: bool = False,
    ):
        sig = inspect.signature(fn)

        missing = missing if missing is not None else set(self.params)
        invalid_params = set() if invalid_params is None else invalid_params

        skip_missing = (
            any([p.kind == VAR_KEYWORD for p in sig.parameters.values()])
            if skip_missing is None
            else skip_missing
        )

        for m in self.params:
            if not allow_miss:
                p = sig.parameters[m]
            else:
                p = sig.parameters.get(m) # type: ignore
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
        fn,
        missing: set[str] | None = None,
        invalid_params: set[str] | None = None,
        skip_missing: bool | None = None,
        allow_miss: bool = False,
    ):
        # copy sequence to check for missing parameter names
        missing, invalid_params, skip_missing = self.__check_with_missing(
            fn, missing, invalid_params, skip_missing, allow_miss
        )

        if invalid_params:
            raise InvalidParametersError(invalid_params)

        if missing and not skip_missing:
            raise MissingKeywordsError(missing)

    def __warn(self, kw_name: str):
        msg = ""
        if self.display_kw:
            msg += 'Parameter "%s" ' % kw_name

        if self.message_is_dict:
            msg += self.message.get(kw_name, self.default_message)  # type: ignore
        else:
            msg += self.message  # type: ignore

        warnings.warn(msg, self.category, stacklevel=self.stacklevel + 1)

    @overload
    def __call__(self, arg: type[_T]) -> type[_T]: ...

    @overload
    def __call__(self, arg: Callable[_P, _T]) -> Callable[_P, _T]: ...

    # Mirrors python's deprecated wrapper with a few changes
    def __call__(self, arg: type[_T] | Callable[_P, _T]) -> type[_T] | Callable[_P, _T]:
        not_dispatched = self.params.copy()


        def check_kw_arguments(kw: dict):
            nonlocal not_dispatched
            if not_dispatched:
                for k in kw.keys():
                    print(k, not_dispatched)
                    if k in not_dispatched:
                        self.__warn(k)
                        # remove after so we don't repeat
                        not_dispatched.remove(k)

        if isinstance(arg, type):
            # NOTE: Combining init and new together is done to
            # solve deprecation of both new_args and init_args

            missing, invalid_params, skip_missing = self.__check_with_missing(
                arg, allow_miss=True
            )

            original_new = arg.__new__
            self.__check_for_missing_kwds(
                original_new, missing, invalid_params, skip_missing, allow_miss=True
            )

            @wraps(original_new)
            def __new__(cls, /, *args, **kwargs):
                check_kw_arguments(kwargs)
                if original_new is not object.__new__:
                    return original_new(cls, *args, **kwargs)
                # Python Comment: Mirrors a similar check in object.__new__.
                elif cls.__init__ is object.__init__ and (args or kwargs):
                    raise TypeError(f"{cls.__name__}() takes no arguments")
                else:
                    return original_new(cls)

            arg.__new__ = staticmethod(__new__)  # type: ignore

            original_init_subclass = arg.__init_subclass__
            # Python Comment: We need slightly different behavior if __init_subclass__
            # is a bound method (likely if it was implemented in Python)
            if isinstance(original_init_subclass, MethodType):
                self.__check_for_missing_kwds(
                    original_init_subclass, missing, invalid_params, skip_missing, allow_miss=True
                )
                original_init_subclass = original_init_subclass.__func__

                @wraps(original_init_subclass)
                def __init_subclass__(*args, **kwargs):
                    check_kw_arguments(kwargs)
                    return original_init_subclass(*args, **kwargs)

                arg.__init_subclass__ = classmethod(__init_subclass__)  # type: ignore
            # Python Comment: Or otherwise, which likely means it's a builtin such as
            # object's implementation of __init_subclass__.
            else:

                @wraps(original_init_subclass)
                def __init_subclass__(*args, **kwargs):
                    check_kw_arguments(kwargs)
                    return original_init_subclass(*args, **kwargs)

                arg.__init_subclass__ = __init_subclass__  # type: ignore

            return arg

        elif callable(arg):
            # Check for missing functon arguments
            self.__check_for_missing_kwds(arg)

            @wraps(arg)
            def wrapper(*args, **kwargs):
                check_kw_arguments(kwargs)
                return arg(*args, **kwargs)

            if sys.version_info >= (3, 12):
                if inspect.iscoroutinefunction(arg):
                    wrapper = inspect.markcoroutinefunction(wrapper)

            return wrapper

        else:
            raise TypeError(
                "@deprecated_params decorator with non-None category must be applied to "
                f"a class or callable, not {arg!r}"
            )
