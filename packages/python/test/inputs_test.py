from unittest.mock import patch

import pytest

from diagraph import Depends, Diagraph, OpenAI, prompt


@pytest.fixture(autouse=True)
def _clear_defaults(request):
    Diagraph.set_error(None)
    Diagraph.set_llm(None)
    Diagraph.set_log(None)
    yield
    Diagraph.set_error(None)
    Diagraph.set_llm(None)
    Diagraph.set_log(None)


def describe_inputs():
    def test_it_calls_functions_in_a_diamond():
        def l0():
            return "l0"

        def l1_l(l0: str = Depends(l0)):
            return f"{l0}l1_l"

        def l1_r(l0: str = Depends(l0)):
            return f"{l0}l1_r"

        def l2(l1_l: str = Depends(l1_l), l1_r: str = Depends(l1_r)):
            return f"{l1_l}{l1_r}l2"

        assert Diagraph(l2).run().result == "l0l1_ll0l1_rl2"

    def test_it_calls_functions_in_a_wider_diamond():
        def l0():
            return "l0"

        def l1_l(l0: str = Depends(l0)):
            return f"{l0}l1_l"

        def l1_c(l0: str = Depends(l0)):
            return f"{l0}l1_c"

        def l1_r(l0: str = Depends(l0)):
            return f"{l0}l1_r"

        def l2(
            l1_l: str = Depends(l1_l),
            l1_c: str = Depends(l1_c),
            l1_r: str = Depends(l1_r),
        ):
            return f"{l1_l}{l1_c}{l1_r}l2"

        assert Diagraph(l2).run().result == "l0l1_ll0l1_cl0l1_rl2"

    def test_it_calls_functions_with_multiple_results():
        def l0():
            return "l0"

        def l1_l(l0: str = Depends(l0)):
            return f"{l0}l1_l"

        def l1_r(l0: str = Depends(l0)):
            return f"{l0}l1_r"

        def l2_l(l1_l: str = Depends(l1_l)):
            return f"{l1_l}l2_l"

        def l2_r(l1_r: str = Depends(l1_r)):
            return f"{l1_r}l2_r"

        result = Diagraph(l2_l, l2_r).run().result
        assert result is not None
        assert result[0] == "l0l1_ll2_l"
        assert result[1] == "l0l1_rl2_r"

    def test_it_calls_functions_with_multiple_inputs():
        def d0a():
            return "d0a"

        def d0b():
            return "d0b"

        def d1a(i: str = Depends(d0a)):
            return f"{i}d1a"

        def d1b(i: str = Depends(d0b)):
            return f"{i}d1b"

        def d2(a: str = Depends(d1a), b: str = Depends(d1b)):
            return f"{a}{b}d2"

        assert Diagraph(d2).run().result == "d0ad1ad0bd1bd2"

    def test_it_calls_functions_with_multiple_inputs_and_results():
        def d0a():
            return "d0a"

        def d0b():
            return "d0b"

        def d1a(i: str = Depends(d0a)):
            return f"{i}-d1a"

        def d1b(i: str = Depends(d0b)):
            return f"{i}-d1b"

        def d2(a: str = Depends(d1a), b: str = Depends(d1b)):
            return f"{a}-{b}-d2"

        def d3a(a: str = Depends(d2)):
            return f"{a}-d3a"

        def d3b(a: str = Depends(d2)):
            return f"{a}-d3b"

        result = Diagraph(d3a, d3b).run().result
        assert result is not None
        assert result[0] == "d0a-d1a-d0b-d1b-d2-d3a"
        assert result[1] == "d0a-d1a-d0b-d1b-d2-d3b"

    def test_it_passes_input():
        def d0(input: str):
            return f"{input}_d0"

        def d1a(i: str = Depends(d0)):
            return f"{i}-d1a"

        def d1b(i: str = Depends(d0)):
            return f"{i}-d1b"

        def d2(i1: str = Depends(d1a), i2: str = Depends(d1b)):
            return f"{i1}-{i2}-d2"

        assert Diagraph(d2).run("foo").result == "foo_d0-d1a-foo_d0-d1b-d2"

    def test_it_passes_default_inputs():
        def d0(input: str = "foo"):
            return f"d0:{input}"

        def d1(i0: str = Depends(d0)):
            return f"d1:{i0}"

        assert Diagraph(d1).run().result == "d1:d0:foo"

    def test_it_passes_multiple_default_inputs():
        def d0(foo: str = "foo", bar: str = "bar"):
            return f"d0:{foo}-{bar}"

        def d1(i0: str = Depends(d0)):
            return f"d1:{i0}"

        assert Diagraph(d1).run().result == "d1:d0:foo-bar"

    def test_it_passes_mixed_default_and_non_inputs():
        def d0(foo: str, bar: str = "bar"):
            return f"d0:{foo}-{bar}"

        def d1(i0: str = Depends(d0)):
            return f"d1:{i0}"

        assert Diagraph(d1).run("baz").result == "d1:d0:baz-bar"

    def test_it_passes_input_to_each_fn():
        def d0(input: str):
            return f"{input}_d0"

        def d1a(input: str, i: str = Depends(d0)):
            return f"{input}_{i}-d1a"

        def d1b(input: str, i: str = Depends(d0)):
            return f"{input}_{i}-d1b"

        def d2(
            input: str,
            i1: str = Depends(d1a),
            i2: str = Depends(d1b),
        ):
            return f"{input}_{i1}-{i2}-d2"

        assert Diagraph(d2).run("foo").result == "foo_foo_foo_d0-d1a-foo_foo_d0-d1b-d2"

    def test_it_passes_input_at_end_of_args():
        def d0(input: str):
            return f"d0:{input}"

        def d1a(input: str, d0: str = Depends(d0)):
            return f"d1a:{input}-{d0}"

        def d1b(
            d0: str = Depends(d0),
            input: str = "",
        ):
            return f"d1b:{input}-{d0}"

        def d2(
            input: str,
            d1a: str = Depends(d1a),
            d1b: str = Depends(d1b),
        ):
            return f"d2:{input}-{d1a}-{d1b}"

        dg = Diagraph(d2).run("foo")
        assert dg[d0].result == "d0:foo"
        assert dg[d1a].result == f"d1a:foo-{dg[d0].result}"
        assert dg[d1b].result == f"d1b:foo-{dg[d0].result}"
        assert dg[d2].result == f"d2:foo-{dg[d1a].result}-{dg[d1b].result}"
        assert dg.result == f"d2:foo-{dg[d1a].result}-{dg[d1b].result}"

    def describe_kwargs():
        def test_it_avoids_a_kwargs_complaint_when_using_default():
            def foo(input1: str, input2: int, keyword_arg="some-default"):
                return f'Inputs: "{input1}" "{input2}" {keyword_arg}'

            assert (
                Diagraph(foo).run("input1", 1).result
                == 'Inputs: "input1" "1" some-default'
            )

        def test_it_avoids_a_kwargs_complaint_when_passed_as_an_arg():
            def foo(input1: str, input2: int, keyword_arg="some-default"):
                return f'Inputs: "{input1}" "{input2}" {keyword_arg}'

            assert (
                Diagraph(foo).run("input1", 1, "foobar").result
                == 'Inputs: "input1" "1" foobar'
            )

        def test_it_avoids_a_kwargs_complaint_when_supplied_as_kwarg():
            def foo(input1: str, input2: int, keyword_arg="some-default"):
                return f'Inputs: "{input1}" "{input2}" {keyword_arg}'

            assert (
                Diagraph(foo).run("input1", 1, keyword_arg="foobar").result
                == 'Inputs: "input1" "1" foobar'
            )

    def test_it_passes_input_mixed_all_over_the_args():
        def d0(input: str):
            return f"{input}_d0"

        def d1a(input: str, i: str = Depends(d0)):
            return f"{input}_{i}-d1a"

        def d1b(
            i: str = Depends(d0),
            input: str = "",
        ):
            return f"{input}_{i}-d1b"

        def d2(
            i1: str = Depends(d1a),
            input: str = "",
            i2: str = Depends(d1b),
        ):
            return f"{input}_{i1}-{i2}-d2"

        assert Diagraph(d2).run("foo").result == "foo_foo_foo_d0-d1a-foo_foo_d0-d1b-d2"

    def test_it_ignores_excess_args():
        def d0(input: str):
            return f"{input}_d0"

        def d1a(input: str, i: str = Depends(d0)):
            return f"{input}_{i}-d1a"

        def d1b(
            input: str,
            i: str = Depends(d0),
        ):
            return f"{input}_{i}-d1b"

        def d2(
            i1: str = Depends(d1a),
            input: str = "",
            i2: str = Depends(d1b),
        ):
            return f"{input}_{i1}-{i2}-d2"

        assert (
            Diagraph(d2).run("foo", "bar", "baz").result
            == "foo_foo_foo_d0-d1a-foo_foo_d0-d1b-d2"
        )

    def test_it_passes_multiple_inputs():
        def d0(input_1: str):
            return f"{input_1}_d0"

        def d1a(input_1: str, i: str = Depends(d0), input_2: str = ""):
            return f"{input_1}_{i}-d1a_{input_2}"

        def d1b(
            i: str = Depends(d0),
            input_1: str = "",
        ):
            return f"{input_1}_{i}-d1b"

        def d2(
            i1: str = Depends(d1a),
            input_1: str = "",
            input_2: str = "",
            i2: str = Depends(d1b),
        ):
            return f"{input_1}_{i1}-{i2}-d2_{input_2}"

        assert (
            Diagraph(d2).run("foo", "bar").result
            == "foo_foo_foo_d0-d1a_bar-foo_foo_d0-d1b-d2_bar"
        )

    def test_it_passes_untyped_inputs():
        def d0(input1, input2: str, input3):
            return f"d0:{input1}+{input2}+{input3}"

        def d1a(input1, d0: str = Depends(d0), input2=""):
            return f"d1a:{input1}+{input2}+{d0}"

        def d1b(input1, d0: str = Depends(d0), input2="", input3=""):
            return f"d1b:{input1}+{input2}+{d0}"

        def d2(
            d1a: str = Depends(d1a),
            input1="",
            d1b: str = Depends(d1b),
        ):
            return f"d2:{input1}+{d1a}+{d1b}"

        d0_result = "d0:foo+1+1.5"
        assert (
            Diagraph(d2).run("foo", 1, 1.5).result
            == f"d2:foo+d1a:foo+1+{d0_result}+d1b:foo+1+{d0_result}"
        )

    def test_it_passes_mixed_type_inputs():
        def join_list(input: list[int]):
            return "|".join([str(i) for i in input])

        def join_tuple(input: tuple):
            return ",".join(input)

        def d0(input1: str, input2: list[int], input3: tuple[str]):
            return f"d0:{input1}+{join_list(input2)}+{join_tuple(input3)}"

        def d1a(input1, d0: str = Depends(d0), input2=""):
            return f"d1a:{input1}+{join_list(input2)}+{d0}"

        def d1b(input1, d0: str = Depends(d0), _input2="", input3=""):
            return f"d1b:{input1}+{join_tuple(input3)}+{d0}"

        def d2(
            d1a: str = Depends(d1a),
            input1="",
            d1b: str = Depends(d1b),
        ):
            return f"d2:{input1}+{d1a}+{d1b}"

        arg2 = [1, 2, 3]
        arg3 = ("a", "b")

        d0_result = f"d0:foo+{join_list(arg2)}+{join_tuple(arg3)}"
        d1a_result = f"d1a:foo+{join_list(arg2)}+{d0_result}"
        d1b_result = f"d1b:foo+{join_tuple(arg3)}+{d0_result}"
        assert (
            Diagraph(d2).run("foo", arg2, arg3).result
            == f"d2:foo+{d1a_result}+{d1b_result}"
        )

    def describe_star_args():
        def test_it_passes_star_args():
            def d0(*args):
                args = "|".join(args)
                return f"d0:{args}"

            assert Diagraph(d0).run("foo", "bar", "baz").result == "d0:foo|bar|baz"

        def test_it_passes_star_args_and_input():
            def d1(*args, foo: str):
                args = "|".join(args)
                return f"d1:{args}"

            dg = None
            with pytest.raises(
                Exception,
                match="Errors encountered.",
            ):
                dg = Diagraph(d1)
                dg.run("foo", "bar", "baz")
            assert "Found arguments defined after * args" in str(dg[d1].error)

        def test_it_passes_star_args_after_input():
            def d2(foo, *args):
                args = "|".join(args)
                return f"d2:{foo}|{args}"

            assert Diagraph(d2).run("foo", "bar", "baz").result == "d2:foo|bar|baz"

        def test_it_passes_star_args_after_multiple_input():
            def d3(foo, bar, *args):
                return f"d3:{foo}|{args[0]}"

            assert Diagraph(d3).run("foo", "bar", "baz").result == "d3:foo|baz"

        def test_it_passes_starstar_kwargs():
            def d0(**kwargs):
                args = "|".join(kwargs.values())
                return f"d0:{args}"

            assert (
                Diagraph(d0).run(foo="foo", bar="bar", baz="baz").result
                == "d0:foo|bar|baz"
            )

    def describe_real_world_example():
        def test_it_raises_if_returning_non_from_a_prompt():
            def fake_run(self, string, stream=None, **kwargs):
                return string + "_"

            with patch.object(
                OpenAI,
                "run",
                fake_run,
            ):

                @prompt
                def fn():
                    return None

                with pytest.raises(
                    Exception,
                    match="Errors encountered",
                ):
                    dg = Diagraph(fn).run()
                    assert dg.result is None
                    assert "unsupported operand type(s) for +" in str(dg[fn].error)

        def test_it_does_a_real_world_example_with_prompt_fn():
            def fake_run(self, string, stream=None, **kwargs):
                return string + "_"

            with patch.object(
                OpenAI,
                "run",
                fake_run,
            ):

                @prompt
                def tell_me_a_joke():
                    return "joke"

                @prompt
                def explanation(joke: str = Depends(tell_me_a_joke)) -> str:
                    return f"{joke} explain"

                @prompt
                def improvement(
                    joke: str = Depends(tell_me_a_joke),
                    explanation: str = Depends(explanation),
                ) -> str:
                    return f"{joke} {explanation} improve"

                diagraph = Diagraph(improvement).run()
                assert diagraph.result == "joke_ joke_ explain_ improve_"
                assert diagraph[tell_me_a_joke].result == "joke_"
                assert diagraph[explanation].result == "joke_ explain_"
                assert diagraph[improvement].result == diagraph.result
                assert diagraph[0].result == "joke_"
                assert diagraph[1].result == "joke_ explain_"
                assert diagraph[2].result == diagraph.result
                assert diagraph[-3].result == "joke_"
                assert diagraph[-2].result == "joke_ explain_"
                assert diagraph[-1].result == diagraph.result
                assert diagraph[tell_me_a_joke].prompt == "joke"
                assert diagraph[explanation].prompt == "joke_ explain"
                assert diagraph[improvement].prompt == "joke_ joke_ explain_ improve"
                assert diagraph[0].prompt == "joke"
                assert diagraph[1].prompt == "joke_ explain"
                assert diagraph[2].prompt == "joke_ joke_ explain_ improve"
                assert diagraph[-3].prompt == "joke"
                assert diagraph[-2].prompt == "joke_ explain"
                assert diagraph[-1].prompt == "joke_ joke_ explain_ improve"
