from unittest.mock import patch

import pytest

from diagraph import LLM, Depends, Diagraph, Fn, prompt


def describe_run():
    def test_it_can_run_a_single_fn(mocker):
        mock_instance = mocker.Mock()

        def d0():
            print("d0")
            return mock_instance()

        diagraph = Diagraph(d0)

        assert mock_instance.call_count == 0
        diagraph.run()
        assert mock_instance.call_count == 1

    def test_it_can_run_a_single_dependency(mocker):
        d0_mock = mocker.Mock()
        d0_mock.return_value = "d0"

        def d0():
            return d0_mock()

        d1_mock = mocker.Mock()
        d1_mock.return_value = "d1"

        def d1(d0: str = Depends(d0)):
            return d1_mock(d0)

        diagraph = Diagraph(d1)

        assert d0_mock.call_count == 0
        assert d1_mock.call_count == 0
        diagraph.run()
        assert d0_mock.call_count == 1
        assert d1_mock.call_count == 1
        d1_mock.assert_called_with(d0_mock.return_value)

    def test_it_can_run_two_dependencies(mocker):
        d0_mock = mocker.Mock()
        d0_mock.return_value = "d0"

        def d0():
            return d0_mock()

        d1_mock = mocker.Mock()
        d1_mock.return_value = "d1"

        def d1(d0: str = Depends(d0)):
            return d1_mock(d0)

        d2_mock = mocker.Mock()
        d2_mock.return_value = "d2"

        def d2(d1: str = Depends(d1)):
            return d2_mock(d1)

        diagraph = Diagraph(d2)

        assert d0_mock.call_count == 0
        assert d1_mock.call_count == 0
        assert d2_mock.call_count == 0
        diagraph.run()
        assert d0_mock.call_count == 1
        assert d1_mock.call_count == 1
        assert d2_mock.call_count == 1
        d1_mock.assert_called_with(d0_mock.return_value)
        d2_mock.assert_called_with(d1_mock.return_value)

    def describe_concurrency():
        @patch("time.sleep", return_value=None)
        def test_it_runs_functions_concurrently(patched_time_sleep):
            import time

            def a():
                time.sleep(999)
                return "a"

            def b():
                time.sleep(2)
                return "b"

            def c():
                return "c"

            assert Diagraph(a, b, c).run().result == ("a", "b", "c")
            assert patched_time_sleep.call_count == 2

        @patch("time.sleep", return_value=None)
        def test_it_runs_prompt_functions_concurrently(patched_time_sleep):
            import time

            class MockLLM(LLM):
                times: int
                error: bool

                def __init__(self, times=0, error=False, **kwargs):
                    self.times = times
                    self.kwargs = kwargs
                    self.error = error

                def run(self, prompt, log, model=None, stream=None, **kwargs):
                    response = ""
                    kwargs = {
                        **self.kwargs,
                        **kwargs,
                        "model": model,
                    }
                    response = ""
                    if self.error:
                        raise Exception("test error")
                    log("start", None)

                    for i in range(self.times):
                        i = f"{i}"
                        response += i
                        log("data", i)
                    log("end", None)
                    return response

            @prompt
            def a():
                time.sleep(1)
                return "a"

            @prompt
            def b():
                return "b"

            assert Diagraph(a, b, llm=MockLLM(times=3)).run().result == ("012", "012")

        @patch("time.sleep", return_value=None)
        def test_it_runs_prompt_with_argument_functions_concurrently(
            patched_time_sleep,
        ):
            import time

            class MockLLM(LLM):
                times: int
                error: bool

                def __init__(self, times=0, error=False, **kwargs):
                    self.times = times
                    self.kwargs = kwargs
                    self.error = error

                def run(self, prompt, log, model=None, stream=None, **kwargs):
                    response = ""
                    kwargs = {
                        **self.kwargs,
                        **kwargs,
                        "model": model,
                    }
                    response = ""
                    if self.error:
                        raise Exception("test error")
                    log("start", None)

                    for i in range(self.times):
                        i = f"{i}"
                        response += i
                        log("data", i)
                    log("end", None)
                    return response

            mock_llm_a = MockLLM(times=2)

            @prompt(log=None, llm=mock_llm_a)
            def a():
                time.sleep(999)
                return "a"

            @prompt(log=None, llm=mock_llm_a)
            def b():
                return "b"

            assert Diagraph(a, b).run().result == ("01", "01")

    def test_it_calls_functions_in_order():
        def l0():
            return "foo"

        def l1(l0: str = Depends(l0)):
            return f"{l0}bar"

        def l2(l1: str = Depends(l1)):
            return f"{l1}baz"

        assert Diagraph(l2).run().result == "foobarbaz"

    def test_it_can_get_results_for_non_prompt_functions():
        def l0():
            return "foo"

        def l1(l0: str = Depends(l0)):
            return f"{l0}bar"

        def l2(l1: str = Depends(l1)):
            return f"{l1}baz"

        diagraph = Diagraph(l2)
        assert diagraph.run().result == "foobarbaz"
        assert diagraph[0].result == "foo"
        assert diagraph[1].result == "foobar"
        assert diagraph[2].result == "foobarbaz"

    def describe_a_complicated_graph():
        @pytest.mark.parametrize(
            ("terminal_nodes", "assertions"),
            [
                (
                    "d3a",
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 1),
                        ("d3a", 1),
                        ("d0a", 0),
                        ("d1a", 0),
                        ("d1b", 0),
                        ("d2a", 0),
                        ("d2b", 0),
                        ("d2c", 0),
                    ),
                ),
                (
                    "d2d",
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 1),
                        ("d3a", 0),
                        ("d0a", 0),
                        ("d1a", 0),
                        ("d1b", 0),
                        ("d2a", 0),
                        ("d2b", 0),
                        ("d2c", 0),
                    ),
                ),
                (
                    "d2c",
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 0),
                        ("d1a", 0),
                        ("d1b", 0),
                        ("d2a", 0),
                        ("d2b", 0),
                        ("d2c", 1),
                    ),
                ),
                (
                    "d2b",
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 0),
                        ("d2a", 0),
                        ("d2b", 1),
                        ("d2c", 0),
                    ),
                ),
                (
                    "d2a",
                    (
                        ("d0b", 0),
                        ("d1c", 0),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 0),
                        ("d2a", 1),
                        ("d2b", 0),
                        ("d2c", 0),
                    ),
                ),
                (
                    "d1c",
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 0),
                        ("d1a", 0),
                        ("d1b", 0),
                        ("d2a", 0),
                        ("d2b", 0),
                        ("d2c", 0),
                    ),
                ),
                (
                    "d1b",
                    (
                        ("d0b", 1),
                        ("d1c", 0),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 0),
                        ("d1a", 0),
                        ("d1b", 1),
                        ("d2a", 0),
                        ("d2b", 0),
                        ("d2c", 0),
                    ),
                ),
                (
                    "d1a",
                    (
                        ("d0b", 0),
                        ("d1c", 0),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 0),
                        ("d2a", 0),
                        ("d2b", 0),
                        ("d2c", 0),
                    ),
                ),
                (
                    "d0b",
                    (
                        ("d0b", 1),
                        ("d1c", 0),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 0),
                        ("d1a", 0),
                        ("d1b", 0),
                        ("d2a", 0),
                        ("d2b", 0),
                        ("d2c", 0),
                    ),
                ),
                (
                    "d0a",
                    (
                        ("d0b", 0),
                        ("d1c", 0),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 1),
                        ("d1a", 0),
                        ("d1b", 0),
                        ("d2a", 0),
                        ("d2b", 0),
                        ("d2c", 0),
                    ),
                ),
                (
                    ("d0a", "d1a"),
                    (
                        ("d0b", 0),
                        ("d1c", 0),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 0),
                        ("d2a", 0),
                        ("d2b", 0),
                        ("d2c", 0),
                    ),
                ),
                (
                    ("d0a", "d1a", "d2a"),
                    (
                        ("d0b", 0),
                        ("d1c", 0),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 0),
                        ("d2a", 1),
                        ("d2b", 0),
                        ("d2c", 0),
                    ),
                ),
                (
                    ("d2a", "d2b"),
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 0),
                        ("d2a", 1),
                        ("d2b", 1),
                        ("d2c", 0),
                    ),
                ),
                (
                    ("d2a", "d2b", "d2c"),
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 0),
                        ("d2a", 1),
                        ("d2b", 1),
                        ("d2c", 1),
                    ),
                ),
                (
                    ("d2a", "d2b", "d2d"),
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 1),
                        ("d3a", 0),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 0),
                        ("d2a", 1),
                        ("d2b", 1),
                        ("d2c", 0),
                    ),
                ),
                (
                    ("d2a", "d2b", "d3a"),
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 1),
                        ("d3a", 1),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 0),
                        ("d2a", 1),
                        ("d2b", 1),
                        ("d2c", 0),
                    ),
                ),
                (
                    ("d2a", "d2b", "d2c", "d3a"),
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 1),
                        ("d3a", 1),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 0),
                        ("d2a", 1),
                        ("d2b", 1),
                        ("d2c", 1),
                    ),
                ),
                (
                    ("d2a", "d2b", "d2c", "d3a", "d1b"),
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 1),
                        ("d3a", 1),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 1),
                        ("d2a", 1),
                        ("d2b", 1),
                        ("d2c", 1),
                    ),
                ),
            ],
        )
        def test_it_runs_the_whole_graph(mocker, terminal_nodes, assertions):
            d0a_mock = mocker.Mock(id="d0")
            d0a_mock.return_value = "d0"

            def d0a():
                return d0a_mock()

            d1a_mock = mocker.Mock(id="d1a")
            d1a_mock.return_value = "d1a"

            def d1a(d0a=Depends(d0a)):
                return d1a_mock()

            d0b_mock = mocker.Mock(id="d0b")
            d0b_mock.return_value = "d0b"

            def d0b():
                return d0b_mock()

            d1b_mock = mocker.Mock(id="d1b")
            d1b_mock.return_value = "d1b"

            def d1b(d0b=Depends(d0b)):
                return d1b_mock()

            d1c_mock = mocker.Mock(id="d1c")
            d1c_mock.return_value = "d1c"

            def d1c(d0b=Depends(d0b)):
                return d1c_mock()

            d2a_mock = mocker.Mock(id="d2a")
            d2a_mock.return_value = "d2a"

            def d2a(d1a=Depends(d1a)):
                return d2a_mock()

            d2b_mock = mocker.Mock(id="d2b")
            d2b_mock.return_value = "d2b"

            def d2b(d1a=Depends(d1a), d1c=Depends(d1c)):
                return d2b_mock()

            d2c_mock = mocker.Mock(id="d2c")
            d2c_mock.return_value = "d2c"

            def d2c(d1c=Depends(d1c)):
                return d2c_mock()

            d2d_mock = mocker.Mock(id="d2d")
            d2d_mock.return_value = "d2d"

            def d2d(d1c=Depends(d1c)):
                return d2d_mock()

            d3a_mock = mocker.Mock(id="d3a")
            d3a_mock.return_value = "d3a"

            def d3a(d2d=Depends(d2d)):
                return d3a_mock()

            mocks: dict[str, mocker.Mock] = {
                "d0b": d0b_mock,
                "d1c": d1c_mock,
                "d2d": d2d_mock,
                "d3a": d3a_mock,
                "d0a": d0a_mock,
                "d1a": d1a_mock,
                "d1b": d1b_mock,
                "d2a": d2a_mock,
                "d2b": d2b_mock,
                "d2c": d2c_mock,
            }

            nodes: dict[str, Fn] = {
                "d0b": d0b,
                "d1c": d1c,
                "d2d": d2d,
                "d3a": d3a,
                "d0a": d0a,
                "d1a": d1a,
                "d1b": d1b,
                "d2a": d2a,
                "d2b": d2b,
                "d2c": d2c,
            }

            for key, expectation in assertions:
                expectation = 0
                try:
                    assert mocks[key].call_count == expectation
                except Exception as e:
                    print(
                        f'for key "{key}": expected call count {expectation}, got {mocks[key].call_count}',
                    )
                    raise e

            if isinstance(terminal_nodes, tuple):
                terminal_nodes = tuple([nodes[node] for node in terminal_nodes])
            else:
                terminal_nodes = tuple([nodes[terminal_nodes]])

            Diagraph(*terminal_nodes).run()
            for key, expectation in assertions:
                try:
                    assert mocks[key].call_count == expectation
                except Exception as e:
                    print(
                        f'for key "{key}": expected call count {expectation}, got {mocks[key].call_count}',
                    )
                    raise e

        @pytest.mark.parametrize(
            ("starting_nodes", "assertions"),
            [
                (
                    "d0a",
                    (
                        ("d0a", 2),
                        ("d0b", 1),
                        ("d1a", 2),
                        ("d1b", 1),
                        ("d1c", 1),
                        ("d2a", 2),
                        ("d2b", 2),
                        ("d2c", 1),
                        ("d2d", 1),
                        ("d3a", 1),
                    ),
                ),
                (
                    "d0b",
                    (
                        ("d0a", 1),
                        ("d0b", 2),
                        ("d1a", 1),
                        ("d1b", 2),
                        ("d1c", 2),
                        ("d2a", 1),
                        ("d2b", 2),
                        ("d2c", 2),
                        ("d2d", 2),
                        ("d3a", 2),
                    ),
                ),
                (
                    "d1a",
                    (
                        ("d0a", 1),
                        ("d0b", 1),
                        ("d1a", 2),
                        ("d1b", 1),
                        ("d1c", 1),
                        ("d2a", 2),
                        ("d2b", 2),
                        ("d2c", 1),
                        ("d2d", 1),
                        ("d3a", 1),
                    ),
                ),
                (
                    "d1b",
                    (
                        ("d0b", 1),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 2),
                        ("d1c", 1),
                        ("d2a", 1),
                        ("d2b", 1),
                        ("d2c", 1),
                        ("d2d", 1),
                        ("d3a", 1),
                    ),
                ),
                (
                    "d1c",
                    (
                        ("d0b", 1),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 1),
                        ("d1c", 2),
                        ("d2a", 1),
                        ("d2b", 2),
                        ("d2c", 2),
                        ("d2d", 2),
                        ("d3a", 2),
                    ),
                ),
                (
                    "d2a",
                    (
                        ("d0a", 1),
                        ("d0b", 1),
                        ("d1a", 1),
                        ("d1b", 1),
                        ("d1c", 1),
                        ("d2a", 2),
                        ("d2b", 1),
                        ("d2c", 1),
                        ("d2d", 1),
                        ("d3a", 1),
                    ),
                ),
                (
                    "d2b",
                    (
                        ("d0a", 1),
                        ("d0b", 1),
                        ("d1a", 1),
                        ("d1b", 1),
                        ("d1c", 1),
                        ("d2a", 1),
                        ("d2b", 2),
                        ("d2c", 1),
                        ("d2d", 1),
                        ("d3a", 1),
                    ),
                ),
                (
                    "d2c",
                    (
                        ("d0a", 1),
                        ("d0b", 1),
                        ("d1a", 1),
                        ("d1b", 1),
                        ("d1c", 1),
                        ("d2a", 1),
                        ("d2b", 1),
                        ("d2c", 2),
                        ("d2d", 1),
                        ("d3a", 1),
                    ),
                ),
                (
                    "d2d",
                    (
                        ("d0a", 1),
                        ("d0b", 1),
                        ("d1a", 1),
                        ("d1b", 1),
                        ("d1c", 1),
                        ("d2a", 1),
                        ("d2b", 1),
                        ("d2c", 1),
                        ("d2d", 2),
                        ("d3a", 2),
                    ),
                ),
                (
                    "d3a",
                    (
                        ("d0a", 1),
                        ("d0b", 1),
                        ("d1a", 1),
                        ("d1b", 1),
                        ("d1c", 1),
                        ("d2a", 1),
                        ("d2b", 1),
                        ("d2c", 1),
                        ("d2d", 1),
                        ("d3a", 2),
                    ),
                ),
                # (
                #     ["d3a", "d2b"],
                #     (
                #         ("d0a", 1),
                #         ("d0b", 1),
                #         ("d1a", 1),
                #         ("d1b", 1),
                #         ("d1c", 1),
                #         ("d2a", 1),
                #         ("d2b", 2),
                #         ("d2c", 1),
                #         ("d2d", 1),
                #         ("d3a", 2),
                #     ),
                # ),
            ],
        )
        def test_it_runs_the_whole_graph_with_cached_data(
            mocker,
            starting_nodes,
            assertions,
        ):
            d0a_mock = mocker.Mock(id="d0")
            d0a_mock.return_value = "d0"

            def d0a():
                return d0a_mock()

            d1a_mock = mocker.Mock(id="d1a")
            d1a_mock.return_value = "d1a"

            def d1a(d0a=Depends(d0a)):
                return d1a_mock()

            d0b_mock = mocker.Mock(id="d0b")
            d0b_mock.return_value = "d0b"

            def d0b():
                return d0b_mock()

            d1b_mock = mocker.Mock(id="d1b")
            d1b_mock.return_value = "d1b"

            def d1b(d0b=Depends(d0b)):
                return d1b_mock()

            d1c_mock = mocker.Mock(id="d1c")
            d1c_mock.return_value = "d1c"

            def d1c(d0b=Depends(d0b)):
                return d1c_mock()

            d2a_mock = mocker.Mock(id="d2a")
            d2a_mock.return_value = "d2a"

            def d2a(d1a=Depends(d1a)):
                return d2a_mock()

            d2b_mock = mocker.Mock(id="d2b")
            d2b_mock.return_value = "d2b"

            def d2b(d1a=Depends(d1a), d1c=Depends(d1c)):
                return d2b_mock()

            d2c_mock = mocker.Mock(id="d2c")
            d2c_mock.return_value = "d2c"

            def d2c(d1c=Depends(d1c)):
                return d2c_mock()

            d2d_mock = mocker.Mock(id="d2d")
            d2d_mock.return_value = "d2d"

            def d2d(d1c=Depends(d1c)):
                return d2d_mock()

            d3a_mock = mocker.Mock(id="d3a")
            d3a_mock.return_value = "d3a"

            def d3a(d2d=Depends(d2d)):
                return d3a_mock()

            mocks: dict[str, mocker.Mock] = {
                "d0b": d0b_mock,
                "d1c": d1c_mock,
                "d2d": d2d_mock,
                "d3a": d3a_mock,
                "d0a": d0a_mock,
                "d1a": d1a_mock,
                "d1b": d1b_mock,
                "d2a": d2a_mock,
                "d2b": d2b_mock,
                "d2c": d2c_mock,
            }

            nodes: dict[str, Fn] = {
                "d0b": d0b,
                "d1c": d1c,
                "d2d": d2d,
                "d3a": d3a,
                "d0a": d0a,
                "d1a": d1a,
                "d1b": d1b,
                "d2a": d2a,
                "d2b": d2b,
                "d2c": d2c,
            }

            for key, _ in assertions:
                expectation = 0
                try:
                    assert mocks[key].call_count == expectation
                except Exception as e:
                    print(
                        f'for key "{key}": expected call count {expectation}, got {mocks[key].call_count}',
                    )
                    raise e

            dg = Diagraph(*tuple(nodes.values())).run()

            g = {}
            for key, val in dg.__graph__.graph_def.items():
                g[key.__name__] = [v.__name__ for v in val]
            print(g)

            for key, _ in assertions:
                expectation = 1
                try:
                    assert mocks[key].call_count == expectation
                except Exception as e:
                    print(
                        f'for key "{key}": expected call count {expectation}, got {mocks[key].call_count}',
                    )
                    raise e

            print("------ ")
            dg[nodes[starting_nodes]].run()
            print("------ post run, assert that all are as expected -----")

            for key, expectation in assertions:
                try:
                    assert mocks[key].call_count == expectation
                except Exception as e:
                    print(
                        f'for key "{key}": expected call count {expectation}, got {mocks[key].call_count}',
                    )
                    raise e


def describe_running_from_an_index():
    def test_it_throws_if_running_from_an_index_not_yet_run(mocker):
        def l0():
            return "l0"

        def l1(l0=Depends(l0)):
            return "l1"

        def l2(l1=Depends(l1)):
            return "l2"

        # some_mock=mocker.create_autospec(some)
        # some_mock(1)

        diagraph = Diagraph(l2)

        with pytest.raises(
            Exception,
            match="An ancestor is missing a result, run the traversal first",
        ):
            diagraph[l1].run("foobar")

    def test_it_runs_from_the_first_function_if_specified(mocker):
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1"

        def d2(
            d1: str = Depends(d1),
            input: str = "",
        ):
            return f"{input}_{d1}-d2"

        diagraph = Diagraph(d2)

        diagraph[d0].run("foo")
        assert diagraph.result == "foo_foo_foo_d0-d1-d2"

    def test_it_runs_from_the_second_function_if_results_are_present(mocker):
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1"

        def d2(
            d1: str = Depends(d1),
            input: str = "",
        ):
            return f"{input}_{d1}-d2"

        diagraph = Diagraph(d2).run("foo")

        diagraph[d1].run("bar")
        assert diagraph.result == "bar_bar_foo_d0-d1-d2"

    def test_it_runs_from_the_left_of_a_diamond(mocker):
        def d0(input: str):
            return f"{input}_d0"

        def d1a(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1a"

        def d1b(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1b"

        def d2(
            d1a: str = Depends(d1a),
            d1b: str = Depends(d1b),
            input: str = "",
        ):
            return f"{d1a}*{d1b}*d2_{input}"

        diagraph = Diagraph(d2).run("foo")

        diagraph[d1a].run("bar")
        assert diagraph.result == "*".join(
            [
                "bar_foo_d0-d1a",
                "foo_foo_d0-d1b",
                "d2_bar",
            ],
        )

    def test_it_runs_from_the_first_index_if_provided(mocker):
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1"

        def d2(
            d1: str = Depends(d1),
            input: str = "",
        ):
            return f"{input}_{d1}-d2"

        diagraph = Diagraph(d2)
        diagraph[0].run("foo")
        assert diagraph.result == "foo_foo_foo_d0-d1-d2"
