from unittest.mock import patch

import pytest

from diagraph import Depends, Diagraph, OpenAI, prompt


def describe_prompt():
    def test_it_calls_a_prompt():
        def fake_run(self, string, stream=None, **kwargs):
            return string + "_"

        with patch.object(
            OpenAI,
            "run",
            fake_run,
        ):

            @prompt
            def d0(input: str) -> str:
                return input

            input = "foo"
            diagraph = Diagraph(d0).run(input)
            assert diagraph[d0].prompt == f"{input}"
            assert diagraph[d0].result == f"{input}_"

    def test_it_raises_if_calling_prompt_on_non_decorated_function():
        def d0(input: str) -> str:
            return input

        input = "foo"
        diagraph = Diagraph(d0).run(input)
        prompt = None
        with pytest.raises(
            Exception,
            match="This function has not been decorated with @prompt",
        ):
            prompt = diagraph[d0].prompt
        assert prompt is None

    def test_it_calls_a_prompt_on_layer():
        def fake_run(self, string, stream=None, **kwargs):
            return string + "_"

        with patch.object(
            OpenAI,
            "run",
            fake_run,
        ):

            @prompt
            def d0(input: str) -> str:
                return input

            @prompt
            def d1a(d0: str = Depends(d0)) -> str:
                return f"d1a:{d0}"

            @prompt
            def d1b(d0: str = Depends(d0)) -> str:
                return f"d1b:{d0}"

            input = "foo"
            diagraph = Diagraph(d1a, d1b).run(input)
            assert diagraph[0].prompt == f"{input}"
            assert diagraph[0].result == f"{input}_"
            assert diagraph[1].prompt == (f"d1a:{input}_", f"d1b:{input}_")
            assert diagraph[1].result == (f"d1a:{input}__", f"d1b:{input}__")

    def test_it_calls_a_prompt_on_single_layer():
        def fake_run(self, string, stream=None, **kwargs):
            return string + "_"

        with patch.object(
            OpenAI,
            "run",
            fake_run,
        ):

            @prompt
            def d0a(input: str) -> str:
                return input

            @prompt
            def d0b(input: str) -> str:
                return input

            input = "foo"
            diagraph = Diagraph(d0a, d0b).run(input)
            assert diagraph[0].prompt == (f"{input}", f"{input}")
            assert diagraph[0].result == (f"{input}_", f"{input}_")

    def test_it_stores_non_string_responses_from_prompts():
        def fake_run(self, input, stream=None, **kwargs):
            return "foobar"

        with patch.object(
            OpenAI,
            "run",
            fake_run,
        ):

            @prompt
            def fn_int():
                return 1

            @prompt
            def fn_float():
                return 1.5

            @prompt
            def fn_list():
                return [1, 2, 3]

            @prompt
            def fn_tuple():
                return (1, 2, 3)

            @prompt
            def fn_set():
                return {1, 2, 3}

            class MockClass:
                pass

            @prompt
            def fn_class():
                return MockClass

            mock_class = MockClass()

            @prompt
            def fn_class_instance():
                return mock_class

            diagraph = Diagraph(
                fn_int,
                fn_float,
                fn_list,
                fn_tuple,
                fn_set,
                fn_class,
                fn_class_instance,
            ).run()
            assert diagraph[fn_int].prompt == 1
            assert diagraph[fn_float].prompt == 1.5
            assert diagraph[fn_list].prompt == [1, 2, 3]
            assert diagraph[fn_tuple].prompt == (1, 2, 3)
            assert diagraph[fn_set].prompt == {1, 2, 3}
            assert diagraph[fn_class].prompt == MockClass
            assert diagraph[fn_class_instance].prompt == mock_class
