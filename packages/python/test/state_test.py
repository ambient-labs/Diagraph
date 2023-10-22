import pytest

from diagraph import Depends, Diagraph


def describe_state():
    def test_it_gets_fns():
        def foo():
            return "foo"

        def bar(foo: str = Depends(foo)):
            return "bar"

        dg = Diagraph(bar)
        assert dg[foo].fn == foo
        assert dg[bar].fn == bar

    @pytest.mark.parametrize(
        (
            "match",
            "fn",
        ),
        [
            ("Diagraph has not been run yet", lambda dg, _foo, _bar: dg.result),
            ("No record for", lambda dg, foo, _bar: dg[foo].result),
            ("No record for", lambda dg, _foo, bar: dg[bar].result),
        ],
    )
    def test_it_raises_for_a_missing_result(match, fn):
        def foo():
            return "foo"

        def bar(foo: str = Depends(foo)):
            return "bar"

        dg = Diagraph(bar)
        with pytest.raises(Exception, match=match):
            fn(
                dg,
                foo,
                bar,
            )

    @pytest.mark.parametrize(
        (
            "expectation",
            "fn",
        ),
        [
            ("bar", lambda dg, _foo, _bar: dg.result),
            ("foo", lambda dg, foo, _bar: dg[foo].result),
            ("bar", lambda dg, _foo, bar: dg[bar].result),
        ],
    )
    def test_it_gets_results(expectation, fn):
        def foo():
            return "foo"

        def bar(foo: str = Depends(foo)):
            return "bar"

        dg = Diagraph(bar).run()
        result = fn(dg, foo, bar)
        assert result == expectation

    def test_it_gets_subsequent_results():
        times = 0

        def foo():
            return f"foo{times}"

        def bar(foo: str = Depends(foo)):
            return f"bar{times}"

        dg = Diagraph(bar).run()
        assert dg.result == "bar0"
        assert dg[foo].result == "foo0"
        assert dg[bar].result == "bar0"
        times += 1
        dg.run()
        assert dg.result == "bar1"
        assert dg[foo].result == "foo1"
        assert dg[bar].result == "bar1"
        times += 1
        dg[bar].run()
        assert dg.result == "bar2"
        assert dg[foo].result == "foo1"
        assert dg[bar].result == "bar2"

    def test_that_none_is_a_valid_result():
        def foo():
            return None

        def bar(foo: str = Depends(foo)):
            return None

        dg = Diagraph(bar).run()
        assert dg.result is None
        assert dg[foo].result is None
        assert dg[bar].result is None

    def test_it_clears_out_subsequent_results_when_setting_upstream_result():
        times = 0

        def foo():
            return f"foo{times}"

        def bar(foo: str = Depends(foo)):
            return f"bar{times}"

        dg = Diagraph(bar).run()
        assert dg.result == "bar0"
        assert dg[foo].result == "foo0"
        assert dg[bar].result == "bar0"
        dg[foo].result = "fooo"
        assert dg[foo].result == "fooo"

        with pytest.raises(Exception, match="unset"):
            dg[bar].result
        with pytest.raises(Exception, match="unset"):
            dg.result

    def test_it_clears_out_subsequent_results_when_setting_upstream_function():
        times = 0

        def foo():
            return f"foo{times}"

        def bar(foo: str = Depends(foo)):
            return f"bar{times}"

        dg = Diagraph(bar).run()
        assert dg.result == "bar0"
        assert dg[foo].result == "foo0"
        assert dg[bar].result == "bar0"

        def new_foo():
            return f"new_foo{times}"

        dg[foo] = new_foo

        with pytest.raises(Exception, match="unset"):
            dg.result
        with pytest.raises(Exception, match="unset"):
            dg[foo].result
        with pytest.raises(Exception, match="unset"):
            dg[bar].result

    def test_it_does_not_clear_for_unrelated_branches():
        def d0a():
            return "d0a"

        def d1a(d0a=Depends(d0a)):
            return "d1a"

        def d0b():
            return "d0b"

        def d1b(d0b=Depends(d0b)):
            return "d1b"

        def d2(d1a=Depends(d1a), d1b=Depends(d1b)):
            return "d2"

        dg = Diagraph(d2).run()
        assert dg.result == "d2"
        assert dg[d2].result == "d2"

        dg[d0a].result = "cleared"

        assert dg[d0a].result == "cleared"
        assert dg[d0b].result == "d0b"
        assert dg[d1b].result == "d1b"

        with pytest.raises(Exception, match="unset"):
            dg.result
        with pytest.raises(Exception, match="unset"):
            dg[d1a].result
        with pytest.raises(Exception, match="unset"):
            dg[d2].result

    # test it uses historical records correctly (e.g., set an explicit result, run a child multiple times)
