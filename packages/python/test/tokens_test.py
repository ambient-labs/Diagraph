from unittest.mock import patch

from diagraph import Depends, Diagraph, OpenAI, prompt


def describe_tokens():
    def test_it_calls_tokens():
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

            input = "foo bar"
            diagraph = Diagraph(d0).run(input)
            assert diagraph[d0].tokens == 2

    def test_it_calls_tokens_on_layer():
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
                return f"d1a {d0}"

            @prompt
            def d1b(d0: str = Depends(d0)) -> str:
                return f"d1b {d0}"

            input = "foo bar"
            diagraph = Diagraph(d1a, d1b).run(input)
            assert diagraph[0].tokens == 2
            assert diagraph[1].tokens == (6, 6)

    def test_it_calls_tokens_on_single_layer():
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

            input = "foo bar"
            diagraph = Diagraph(d0a, d0b).run(input)
            assert diagraph[0].tokens == (2, 2)
