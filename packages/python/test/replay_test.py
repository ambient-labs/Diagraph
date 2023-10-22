import pytest

from diagraph import Depends, Diagraph


def describe_replay():
    def test_it_gets_result_from_a_node():
        def d0(input: str):
            return f"{input}_d0"

        def d1a(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1a"

        def d1b(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1b"

        def d2(
            input: str,
            d1a: str = Depends(d1a),
            d1b: str = Depends(d1b),
        ):
            return f"{d1a}_{d1b}-d2_{input}"

        diagraph = Diagraph(d2).run("foo")

        assert diagraph[d1a].result == "foo_foo_d0-d1a"

    def test_it_allows_execution_from_final_node_if_previous_result_is_explicitly_set():
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1"

        def d2(input: str, d1: str = Depends(d1)):
            return f"{d1}-d2-{input}"

        diagraph = Diagraph(d2)

        diagraph[d1].result = "newresult"

        diagraph[d2].run("bar")
        assert diagraph.result == "newresult-d2-bar"

    def test_it_modifies_result():
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1"

        def d2(
            input: str,
            d1: str = Depends(d1),
        ):
            return f"{input}_{d1}-d2"

        diagraph = Diagraph(d2)

        diagraph[d1].result = "newresult"

        diagraph[d2].run("bar")
        assert diagraph.result == "bar_newresult-d2"

    def test_it_modifies_result_and_can_replay_in_a_diamond():
        def d0(input: str):
            return f"{input}_d0"

        def d1a(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1a"

        def d1b(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1b"

        def d2(
            input: str,
            d1a: str = Depends(d1a),
            d1b: str = Depends(d1b),
        ):
            return "*".join(
                [
                    d1a,
                    d1b,
                    "d2",
                    input,
                ],
            )

        diagraph = Diagraph(d2).run("foo")

        diagraph[d0].result = "newresult"

        with pytest.raises(Exception, match="unset"):
            diagraph[d1a].result
        with pytest.raises(Exception, match="unset"):
            diagraph[d1b].result
        with pytest.raises(Exception, match="unset"):
            diagraph[d2].result

        diagraph[d1b].result = "d1b"

        diagraph[d1a].run("bar")

        assert diagraph.result == "*".join(
            [
                "bar_newresult-d1a",
                "d1b",
                "d2",
                "bar",
            ],
        )

    def test_it_modifies_prompt_and_can_replay():
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1"

        def d2(
            input: str,
            d1: str = Depends(d1),
        ):
            return f"{d1}-d2_{input}"

        diagraph = Diagraph(d2).run("foo")

        def new_fn(input: str):
            return f"newfn{input}"

        diagraph[d0] = new_fn

        diagraph.run("bar")
        assert diagraph.result == "bar_newfnbar-d1-d2_bar"

    def test_it_modifies_prompt_and_can_replay_multiple_times():
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1"

        def d2(
            input: str,
            d1: str = Depends(d1),
        ):
            return f"{d1}-d2_{input}"

        diagraph = Diagraph(d2).run("foo")

        def new_fn(input: str):
            return f"newfn{input}"

        diagraph[d0] = new_fn

        diagraph.run("bar")
        assert diagraph.result == "bar_newfnbar-d1-d2_bar"

        def new_fn2(input: str):
            return f"newfn2{input}"

        diagraph[d0] = new_fn2

        assert diagraph.run("bar").result == "bar_newfn2bar-d1-d2_bar"
