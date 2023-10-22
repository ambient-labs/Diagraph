import functools
import inspect
from collections.abc import Callable
from textwrap import dedent

import pytest

from ...utils.depends import Depends
from .get_fn import dump_fn, get_fn


def getsource(fn: Callable):
    return dedent(inspect.getsource(fn))


def describe_get_fn():
    def test_it_returns_a_function():
        fn = get_fn("def foo():\n    return 'foo'")
        assert callable(fn)
        assert fn() == "foo"

    def test_it_returns_a_function_from_a_stringified_function():
        def foo():
            return "foo"

        fn = get_fn(getsource(foo))
        assert fn() == "foo"

    def test_it_returns_a_function_from_a_fn_with_an_arg():
        def foo(arg1):
            return f"foo: {arg1}"

        fn = get_fn(getsource(foo))
        assert fn("a") == "foo: a"

    def test_it_returns_a_function_from_a_fn_with_multiple_args():
        def foo(arg1, arg2):
            return f"foo: {arg1} {arg2}"

        fn = get_fn(getsource(foo))
        assert fn("a", "b") == "foo: a b"

    def test_it_returns_a_function_from_a_fn_with_kwargs():
        def foo(arg1="arg1"):
            return f"foo: {arg1}"

        fn = get_fn(getsource(foo))
        assert fn() == "foo: arg1"
        assert fn("a") == "foo: a"

    def test_it_returns_a_function_from_a_fn_with_args_and_kwargs():
        def foo(arg1, arg2, kwarg1="kwarg1"):
            return f"foo: {arg1} {arg2} {kwarg1}"

        fn = get_fn(getsource(foo))
        assert fn("a", "b") == "foo: a b kwarg1"
        assert fn("a", "b", "kw1") == "foo: a b kw1"

        # raise on missing arg
        with pytest.raises(Exception, match="foo"):
            fn("a")

    def test_it_returns_a_function_with_typed_arg():
        def foo(arg1: str):
            return f"foo: {arg1}"

        fn = get_fn(getsource(foo))
        assert fn("a") == "foo: a"

    def test_it_returns_a_function_with_multiple_typed_arg():
        def foo(arg1: str, arg2: int):
            return f"foo: {arg1} {arg2}"

        fn = get_fn(getsource(foo))
        assert fn("a", 1) == "foo: a 1"

    def test_it_returns_a_function_with_typed_kwarg():
        def foo(arg1: str = "arg1"):
            return f"foo: {arg1}"

        fn = get_fn(getsource(foo))
        assert fn() == "foo: arg1"

    def test_it_returns_function_with_a_decorator():
        def decorate(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                return f"decorated: {result}"

            return wrapper

        @decorate
        def foo(arg1: str = "arg1"):
            return f"foo: {arg1}"

        # make sure it's decorated correctly
        assert foo("a") == "decorated: foo: a"

        fn = get_fn(dedent(inspect.getsource(foo)), "foo", {"decorate": decorate})
        assert fn() == "decorated: foo: arg1"
        assert fn("a") == "decorated: foo: a"

    def test_it_returns_function_with_a_decorator_called_with_args():
        def decorate(**decorator_kwargs):
            def decorator(func):
                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    result = func(*args, **kwargs)
                    return f"decorated: {result} {decorator_kwargs}"

                return wrapper

            return decorator

        @decorate(foo="foo")
        def foo(arg1: str = "arg1"):
            return f"foo: {arg1}"

        # make sure it's decorated correctly
        assert foo("a") == "decorated: foo: a {'foo': 'foo'}"

        fn = get_fn(dedent(inspect.getsource(foo)), "foo", {"decorate": decorate})
        assert fn() == "decorated: foo: arg1 {'foo': 'foo'}"
        assert fn("a") == "decorated: foo: a {'foo': 'foo'}"


def describe_dump_fn():
    def test_it_dumps_fn():
        def foo():
            return "foo"

        assert dump_fn(foo) == '''def foo():\n    return "foo"'''

    def test_it_does_not_rewrite_arg():
        def foo(a: int = 1):
            return "foo"

        assert dump_fn(foo) == '''def foo(a: int = 1):\n    return "foo"'''

    def test_it_does_not_rewrite_depends_string_arg():
        def foo(a=Depends("a")):
            return "foo"

        assert dump_fn(foo) == '''def foo(a=Depends("a")):\n    return "foo"'''

    def test_it_does_rewrite_depends_fn_arg():
        def a():
            return "a"

        def foo(a=Depends(a)):
            return "foo"

        assert dump_fn(foo) == '''def foo(a=Depends("a")):\n    return "foo"'''

    def test_it_does_rewrite_multiple_depends_fn_arg():
        def a():
            return "a"

        def b():
            return "b"

        def c():
            return "x"

        def foo(a=Depends(a), b=Depends(b), c=Depends(c)):
            return "foo"

        assert (
            dump_fn(foo)
            == '''def foo(a=Depends("a"), b=Depends("b"), c=Depends("c")):\n    return "foo"'''
        )
