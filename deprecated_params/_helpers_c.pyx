# cython: free_threading = True

cimport cython
from cpython.dict cimport PyDict_GetItem, PyDict_GetItemWithError
from cpython.exc cimport PyErr_WarnEx
from cpython.mapping cimport PyMapping_Check
from cpython.object cimport (PyCallable_Check, PyObject, PyObject_Call,
                             PyObject_Not)
from cpython.sequence cimport  PySequence_GetItem
from cpython.set cimport (PySet_Add, PySet_Discard,
                        PySet_New)
from cpython.unicode cimport PyUnicode_Check

import functools
import inspect
import sys
import types


# It's safer to call for it this way anyways...
cdef object inspect_signature = getattr(inspect, "signature")
cdef object inspect_iscoroutinefunction = getattr(inspect, "iscoroutinefunction", None)
cdef object inspect_markcoroutinefunction = getattr(inspect, "markcoroutinefunction", None)

cdef object functools_wraps = functools.wraps


cdef extern from "Python.h":
    object PyObject_CallOneArg(object, object)


@cython.internal
cdef class _C:
    def _m(self): pass 

cdef object types_MethodType = getattr(types, "MethodType", type(_C()._m))

# TODO: An aiohttp styled cython writer would be a good idea here as well...


DEF KEYWORD_ONLY = 3
DEF VAR_KEYWORD = 4

@cython.internal
cdef class _KeywordsBaseException(Exception):
    cdef frozenset _keywords
    def __init__(self, set keywords, *args) -> None:
        self._keywords = frozenset(keywords)
        super().__init__(*args)

    @property
    def keywords(self):
        """tells what keywords were bad"""
        return self._keywords

    @keywords.setter
    def keywords(self, _: frozenset[str]) -> None:
        """Throws ValueError because keywords is an
        immutable property that shouldn't be edited."""
        raise ValueError("keywords property is immutable")

cdef class MissingKeywordsError(_KeywordsBaseException):
    """Raised when Missing a keyword for an argument"""

    def __init__(self, set keywords, *args) -> None:
        super().__init__(
            keywords,
            f"Missing Keyword arguments for: {list(keywords)!r}",
            *args,
        )


cdef class InvalidParametersError(_KeywordsBaseException):
    """Raised when Parameters were positional arguments without defaults or keyword arguments"""

    def __init__(self, set keywords, *args) -> None:
        super().__init__(
            keywords,
            f"Arguments :{list(keywords)!r} should not be positional",
            *args,
        )


cdef object join_version_if_sequence(object ver):
    if PyUnicode_Check(ver):
        # Quick escape
        return ver
    # fastest way without needing a special api
    return f"{PySequence_GetItem(ver, 0)}.{PySequence_GetItem(ver, 1)}.{PySequence_GetItem(ver, 2)}"

cdef dict convert_removed_in_sequences(
    dict removed_in
):
    return {k: join_version_if_sequence(v) for k, v in removed_in.items()}


cdef class deprecated_params:
    """
    A Wrapper inspired by python's wrapper deprecated from 3.13
    and is used to deprecate parameters
    """

    cdef: 
        set params
        object message
        bint message_is_dict
        bint display_kw
        object category
        Py_ssize_t stacklevel
        object default_message
        dict removed_in


    def __init__(
        self,
        object params,
        object message = "is deprecated",
        /,
        *,
        # default_message should be utilized when a keyword isn't
        # given in message if messaged is defined as a dictionary.
        object default_message = None,
        object category = DeprecationWarning,
        Py_ssize_t stacklevel = 3,
        bint display_kw = True,
        # removed_in is inspired by the deprecation library
        object removed_in = None,
    ) -> None:
        """
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
        :param stacklevel: What level should this wanring appear at? Default: 3
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
      
        if not isinstance(message, (str, dict)):
            raise TypeError(
                f"Expected an object of type str or dict or Mappable type for 'message', not {type(message).__name__!r}"
            )

        if not PyUnicode_Check(params):
            self.params = set(params)
        else:
            self.params = PySet_New((params,))

        
        self.message = message or "is deprecated"
        self.message_is_dict = isinstance(message, dict)

        self.display_kw = display_kw
        self.category = category
        self.stacklevel = stacklevel
        self.default_message = default_message or "do not use"

        if removed_in:
            # Faster to check for PyMapping than Dict alone
            if PyMapping_Check(removed_in):
                # Some people might be more comfortable giving versions in tuples or lists.
                self.removed_in = convert_removed_in_sequences(removed_in)
            else:
                # single removed version meaning that all parameters will be removed in this version
                ver = join_version_if_sequence(removed_in)
                self.removed_in = {k: ver for k in params}
        else:
            self.removed_in = {}

    cdef tuple __check_with_missing(
        self,
        object fn,
        object missing = None,
        object invalid_params = None,
        object skip_missing = None,
        bint allow_miss = False,
    ):
        # NULL Checks can be considered faster...
        cdef PyObject* _p 
        cdef dict params

        sig = PyObject_CallOneArg(inspect_signature, fn)
        params = dict(getattr(sig, "parameters"))

        missing = missing if missing is not None else set(self.params)
        if PyObject_Not(invalid_params):
            invalid_params = set()

        if skip_missing is None:
            for p in params.values():
                if <int>(p.kind) == VAR_KEYWORD:
                    skip_missing = True
                    break

        if not allow_miss:
            for m in self.params:
                _p = PyDict_GetItemWithError(params, m)
                if _p is NULL:
                    raise 

                p = <object>_p

                # Check if were keyword only or aren't carrying a default param
                if int(p.kind) != KEYWORD_ONLY:
                    # Anything this isn't a keyword should be considered as deprecated
                    # as were still technically using it.
                    if PySet_Add(invalid_params, p.name) < 0:
                        raise

                if PyObject_Not(skip_missing):
                    PySet_Discard(missing, p.name)
        else:
            
            for m in self.params:
                _p = PyDict_GetItem(params, m)
                if _p is NULL:
                    # ignore like it's nothing...
                    continue

                p = <object>_p

                # Check if were keyword only or aren't carrying a default param
                if int(p.kind) != KEYWORD_ONLY:
                    # Anything this isn't a keyword should be considered as deprecated
                    # as were still technically using it.
                    if PySet_Add(invalid_params, p.name) < 0:
                        raise

                if PyObject_Not(skip_missing):
                    PySet_Discard(missing, p.name)


        return missing, invalid_params, skip_missing
    
    cdef int __warn(self, kw_name: str) except -1:
        cdef PyObject* obj
        cdef str msg = ""
        if self.display_kw:
            msg += 'Parameter "%s" ' % kw_name
        if self.message_is_dict:
            obj = PyDict_GetItem(self.message, kw_name) 
            if obj != NULL:
                msg += <object>obj
            else:
                msg += self.default_message  # type: ignore
        else:
            msg += self.message  # type: ignore
        if self.removed_in:
            if kw_removed_in := self.removed_in.get(kw_name):
                msg += " [Removed In: "
                msg += kw_removed_in
                msg += "]"
        return PyErr_WarnEx(self.category, msg.encode('utf-8'), stacklevel=self.stacklevel)

    cdef object __check_for_missing_kwds(
        self,
        object fn,
        object missing = None, 
        object invalid_params = None,
        object skip_missing = None,
        bint allow_miss = False,
    ):
        # copy sequence to check for missing parameter names
        missing, invalid_params, skip_missing = self.__check_with_missing(
            fn, missing, invalid_params, skip_missing, allow_miss
        )

        if invalid_params:
            raise InvalidParametersError(invalid_params)

        if missing and not skip_missing:
            raise MissingKeywordsError(missing)



    def __call__(
        self, object arg
    ):
        not_dispatched = self.params.copy()

        def check_kw_arguments(dict kw) -> None:
            nonlocal self
            nonlocal not_dispatched
            if not_dispatched:
                for k in kw.keys():
                    if k in not_dispatched:
                        if self.__warn(k) < 0:
                            raise
                        # remove after so we don't repeat
                        PySet_Discard(not_dispatched, k)

        if isinstance(arg, type):
            # NOTE: Combining init and new together is done to
            # solve deprecation of both new_args and init_args

            missing, invalid_params, skip_missing = self.__check_with_missing(
                arg, None, None, None, allow_miss=True
            )

            original_new = arg.__new__
            self.__check_for_missing_kwds(
                original_new,
                missing,
                invalid_params,
                skip_missing,
                allow_miss=True,
            )

            @functools_wraps(original_new)
            def __new__(
                cls, *args, **kwargs
            ):
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
            if isinstance(original_init_subclass, types_MethodType):
                self.__check_for_missing_kwds(
                    original_init_subclass,
                    missing,
                    invalid_params,
                    skip_missing,
                    allow_miss=True,
                )
                original_init_subclass = original_init_subclass.__func__

                @functools_wraps(original_init_subclass)
                def __init_subclass__(
                    *args, **kwargs
                ):
                    check_kw_arguments(kwargs)
                    return PyObject_Call(original_init_subclass, args, kwargs)

                arg.__init_subclass__ = classmethod(__init_subclass__)  # type: ignore
            # Python Comment: Or otherwise, which likely means it's a builtin such as
            # object's implementation of __init_subclass__.
            else:

                @functools_wraps(original_init_subclass)
                def __init_subclass__(
                    *args, **kwargs
                ) -> None:
                    check_kw_arguments(kwargs)
                    return PyObject_Call(original_init_subclass, args, kwargs)

                arg.__init_subclass__ = __init_subclass__  # type: ignore

            return arg

        elif PyCallable_Check(arg):
            # Check for missing function arguments
            self.__check_for_missing_kwds(arg)

            @functools_wraps(arg)
            def wrapper(*args, **kwargs):
                check_kw_arguments(kwargs)
                return PyObject_Call(arg, args, kwargs)

            if sys.version_info >= (3, 12):
                if inspect_iscoroutinefunction(arg):
                    wrapper = inspect_markcoroutinefunction(wrapper)

            return wrapper

        else:
            raise TypeError(
                "@deprecated_params decorator with non-None category must be applied to "
                f"a class or callable, not {arg!r}"
            )
