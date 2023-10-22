import pytest

from ..classes.diagraph import Diagraph
from .build_parameters import build_parameters
from .depends import Depends


def describe_build_parameters():
    def test_it_builds_empty_parameters():
        def foo():
            return "foo"

        diagraph = Diagraph(foo)
        assert build_parameters(diagraph, foo, (), {}) == ([], {})

    def test_it_raises_when_function_demands_unsupplied_input():
        def foo(input: str):
            return "foo"

        diagraph = Diagraph(foo)
        with pytest.raises(
            Exception,
            match='No argument provided for "input" in function foo.',
        ):
            build_parameters(diagraph, foo, (), {})

    def test_it_raises_when_function_demands_unsupplied_second_input():
        def foo(input: str, bar: str):
            return "foo"

        diagraph = Diagraph(foo)
        with pytest.raises(
            Exception,
            match='No argument provided for "bar" in function foo',
        ):
            build_parameters(diagraph, foo, ("foo",), {})

    def test_it_builds_a_string_arg():
        def foo(input: str):
            return "foo"

        diagraph = Diagraph(foo)
        assert build_parameters(diagraph, foo, ("foo",), {}) == (["foo"], {})

    def test_it_builds_multiple_string_args():
        def foo(foo: str, bar: str):
            return "foo"

        diagraph = Diagraph(foo)
        assert build_parameters(
            diagraph,
            foo,
            (
                "foo",
                "bar",
            ),
            {},
        ) == (["foo", "bar"], {})

    def test_it_handles_single_default():
        def foo(foo: str = "foo"):
            return "foo"

        diagraph = Diagraph(foo)
        assert build_parameters(
            diagraph,
            foo,
            (),
            {},
        ) == ([], {})

    def test_it_handles_multiple_defaults():
        def foo(foo: str = "foo", bar="bar"):
            return "foo"

        diagraph = Diagraph(foo)
        assert build_parameters(
            diagraph,
            foo,
            (),
            {},
        ) == ([], {})

    def test_it_handles_mixed_defaults():
        def foo(foo: str, bar="bar"):
            return "foo"

        diagraph = Diagraph(foo)
        assert build_parameters(
            diagraph,
            foo,
            ("foo",),
            {},
        ) == (["foo"], {})

    def test_it_handles_star_args():
        def foo(*args):
            return "foo"

        diagraph = Diagraph(foo)
        assert build_parameters(
            diagraph,
            foo,
            ("foo", "bar"),
            {},
        ) == (["foo", "bar"], {})

    def test_it_handles_star_args_after_supplied_args():
        def foo(foo: str, *args):
            return "foo"

        diagraph = Diagraph(foo)
        assert build_parameters(
            diagraph,
            foo,
            ("foo", "bar"),
            {},
        ) == (["foo", "bar"], {})

    def test_it_handles_star_args_after_fully_supplied_args():
        def foo(foo: str, bar: str, *args):
            return "foo"

        diagraph = Diagraph(foo)
        assert build_parameters(
            diagraph,
            foo,
            ("foo", "bar"),
            {},
        ) == (["foo", "bar"], {})

    def test_it_handles_star_args_with_default():
        def foo(foo: str = "foo2", *args):
            return "foo"

        diagraph = Diagraph(foo)
        assert build_parameters(
            diagraph,
            foo,
            (),
            {},
        ) == ([], {})

    # def test_it_handles_star_args_with_default_if_supplied():
    #     def foo(foo: str = "foo2", *args):
    #         return "foo"

    #     diagraph = Diagraph(foo)
    #     assert build_parameters(
    #         diagraph,
    #         foo,
    #         ("foo",),
    #         {},
    #     ) == (["foo"], {})

    # def test_it_handles_star_args_with_default_if_supplied_with_star_args():
    #     def foo(foo: str = "foo2", *args):
    #         return "foo"

    #     diagraph = Diagraph(foo)
    #     assert build_parameters(
    #         diagraph,
    #         foo,
    #         ("foo", "bar"),
    #         {},
    #     ) == (["foo", "bar"], {})

    # def test_it_handles_star_args_at_beginning():
    #     def foo(foo: str, bar: str, *args, baz: str):
    #         return "foo"

    #     diagraph = Diagraph(foo)
    #     with pytest.raises(Exception, match="Found arguments defined after "):
    #         build_parameters(
    #             diagraph,
    #             foo,
    #             ("foo", "bar"),
    #             {},
    #         )

    def test_it_handles_depends():
        def foo():
            return "foo"

        def bar(foo=Depends(foo)):
            return "foo"

        diagraph = Diagraph(bar)
        diagraph[foo].result = "foo"
        assert build_parameters(
            diagraph,
            bar,
            ("foo",),
            {},
        ) == ([], {"foo": "foo"})

    def test_it_handles_depends_with_preceding_string_arg():
        def foo():
            return "foo"

        def bar(i1: str, foo=Depends(foo)):
            return "foo"

        diagraph = Diagraph(bar)
        diagraph[foo].result = "foo"
        assert build_parameters(
            diagraph,
            bar,
            ("i1",),
            {},
        ) == (["i1"], {"foo": "foo"})

    def test_it_handles_depends_with_succeding_string_arg():
        def foo():
            return "foo"

        def bar(foo=Depends(foo), i1: str = "i1"):
            return "foo"

        diagraph = Diagraph(bar)
        diagraph[foo].result = "foo"
        assert build_parameters(
            diagraph,
            bar,
            ("i1",),
            {},
        ) == (
            [],
            {"i1": "i1", "foo": "foo"},
        )

    def test_it_handles_depends_with_preceding_and_succeding_string_arg():
        def foo():
            return "foo"

        def bar(i1: str = "i1", foo=Depends(foo), i2: str = "i2"):
            return "foo"

        diagraph = Diagraph(bar)
        diagraph[foo].result = "foo"
        assert build_parameters(
            diagraph,
            bar,
            ("i1", "i2"),
            {},
        ) == ([], {"i1": "i1", "i2": "i2", "foo": "foo"})

    def test_it_handles_depends_with_preceding_and_default_string_arg():
        def foo():
            return "foo"

        def bar(i1: str = "i1", foo=Depends(foo), i2: str = "i2"):
            return "foo"

        diagraph = Diagraph(bar)
        diagraph[foo].result = "foo"
        assert build_parameters(
            diagraph,
            bar,
            ("i1",),
            {},
        ) == ([], {"i1": "i1", "foo": "foo"})

    # def test_it_handles_depends_with_preceding_and_default_string_arg_and_star_args():
    #     def foo():
    #         return "foo"

    #     def bar(i1: str = "i1", foo=Depends(foo), i2: str = "i2", *args):
    #         return "foo"

    #     diagraph = Diagraph(bar)
    #     diagraph[foo].result = "foo"
    #     assert build_parameters(
    #         diagraph,
    #         bar,
    #         ("i1", "i3", "baz"),
    #         {},
    #     ) == (["i1", "foo", "i3", "baz"], {})
