import pytest
from typing import Optional
from deprecated_params import deprecated_params
import sys


# should carry w x y
def test_deprecated_param() -> None:
    @deprecated_params(["x"], "is deprecated")
    def my_func(w: int, *, x: int = 0, y: int = 0) -> None:
        pass

    with pytest.warns(DeprecationWarning, match='Parameter "x" is deprecated'):
        my_func(0, x=0)


def test_deprecated_param_removed_in() -> None:
    @deprecated_params(["x"], "is deprecated", removed_in={"x": (0, 1, 5)})
    def my_func(w: int, *, x: int = 0, y: int = 0) -> None:
        pass

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


class TornadoWarning(DeprecationWarning):
    pass


@pytest.mark.skipif(sys.version_info < (3, 10), reason="kw_only not on 3.9")
def test_dataclasses_with_wrapper_message_dicts_custom_warning() -> None:
    from dataclasses import dataclass, field

    @deprecated_params(
        ["foo"],
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


# TODO: Metaclasses...
