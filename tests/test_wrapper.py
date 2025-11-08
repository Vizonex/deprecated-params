import pytest
from typing import Optional
from deprecated_params import deprecated_params
import sys
import warnings


# should carry w x y
def test_deprecated_param() -> None:
    @deprecated_params(["x"], "is deprecated")
    def my_func(w: int, *, x: int = 0, y: int = 0) -> None:
        pass

    with pytest.warns(DeprecationWarning, match='Parameter "x" is deprecated'):
        my_func(0, x=0)


def test_single_deprecated_param() -> None:
    @deprecated_params("x", "is deprecated")
    def my_func(w: int, *, x: int = 0, y: int = 0) -> None:
        pass

    with pytest.warns(DeprecationWarning, match='Parameter "x" is deprecated'):
        my_func(0, x=0)


def test_no_warn_if_deprecated_parameter_not_passed() -> None:
    @deprecated_params("x", "is deprecated")
    def my_func(w: int, *, x: int = 0, y: int = 0) -> None:
        pass

    # Do not raise or print a warning when X is not passed...
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        my_func(1, y=0)


def test_deprecated_param_removed_in() -> None:
    @deprecated_params(["x"], "is deprecated", removed_in={"x": (0, 1, 5)})
    def my_func(w: int, *, x: int = 0, y: int = 0) -> None:
        pass

    with pytest.warns(
        DeprecationWarning,
        match=r"Parameter \"x\" is deprecated \[Removed In\: 0.1.5\]",
    ):
        my_func(0, x=0)


def test_deprecated_params_dunder_attribute() -> None:
    @deprecated_params(["x"], "is deprecated", removed_in={"x": (0, 1, 5)})
    def my_func(w: int, *, x: int = 0, y: int = 0) -> None:
        pass

    assert getattr(my_func, "__deprecated_params__") == {
        "x": 'Parameter "x" is deprecated [Removed In: 0.1.5]'
    }


# Since 0.2.0 we no longer repeat warnings once. We do it
# so that developers are more willing to remove specific keyword parameters
def test_deprecated_param_repeat_twice() -> None:
    @deprecated_params(["x"], "is deprecated", removed_in={"x": (0, 1, 5)})
    def my_func(w: int, *, x: int = 0, y: int = 0) -> None:
        pass

    with pytest.warns(
        DeprecationWarning,
        match=r"Parameter \"x\" is deprecated \[Removed In\: 0.1.5\]",
    ):
        my_func(0, x=0)

    with pytest.warns(
        DeprecationWarning,
        match=r"Parameter \"x\" is deprecated \[Removed In\: 0.1.5\]",
    ):
        my_func(0, x=0)


def test_class_wrapper_and_kw_display_disabled() -> None:
    @deprecated_params(["foo"], "foo is deprecated", display_kw=False)
    class MyClass:
        def __init__(self, spam: str, *, foo: Optional[str] = None):
            self.spam = spam
            self.foo = foo

    mc = MyClass("spam")
    assert mc.spam == "spam"
    assert mc.foo is None

    with pytest.warns(DeprecationWarning, match="foo is deprecated"):
        MyClass("spam", foo="foo")


def test_class_wrapper_and_kw_display_disabled_one_param() -> None:
    @deprecated_params("foo", "foo is deprecated", display_kw=False)
    class MyClass:
        def __init__(self, spam: str, *, foo: Optional[str] = None):
            self.spam = spam
            self.foo = foo

    mc = MyClass("spam")
    assert mc.spam == "spam"
    assert mc.foo is None

    with pytest.warns(DeprecationWarning, match="foo is deprecated"):
        MyClass("spam", foo="foo")


# There was nothing sillier than this...
class TornadoWarning(DeprecationWarning):
    pass


@pytest.mark.skipif(sys.version_info < (3, 10), reason="kw_only not on 3.9")
def test_dataclasses_with_wrapper_message_dicts_custom_warning() -> None:
    from dataclasses import dataclass, field

    @deprecated_params(
        ["foo", "spam"],
        {"foo": "got foo", "spam": "got spam"},
        display_kw=False,
        category=TornadoWarning,
    )
    @dataclass
    class Class:
        foo: Optional[str] = field(kw_only=True, default=None)
        spam: Optional[str] = field(kw_only=True, default=None)

    with pytest.warns(TornadoWarning, match="got foo"):
        Class(foo="foo")

    with pytest.warns(TornadoWarning, match="got spam"):
        Class(spam="foo")

    # Do Not raise if class doesn't pass a deprecated parameter
    with warnings.catch_warnings():
        warnings.simplefilter(action="error")
        Class()


# TODO: Metaclasses...
