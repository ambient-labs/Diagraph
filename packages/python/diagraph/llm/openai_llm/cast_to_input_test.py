from unittest.mock import patch


def make_completion(_content: str):
    class Delta:
        content = _content

        def model_dump(self, **kwargs):
            return {"content": self.content}

    class Choice:
        delta = Delta()

    class ChatCompletion:
        choices = [Choice]

    return ChatCompletion()


class FakeGenerator:
    def __init__(self, times):
        self.times = times
        self.current_i = 0

    async def __anext__(self):
        current_i = self.current_i
        if self.times <= current_i:
            raise StopAsyncIteration  # raise at end of iteration

        completion = make_completion(f"{current_i}")

        self.current_i += 1
        return completion

    def __aiter__(self):
        return self


class ACompletions:
    def __init__(self, times=1):
        self.times = times

    async def create(self, **kwargs):
        return FakeGenerator(self.times)


def iterable(times=0):
    for i in range(times):
        yield make_completion(f"{i}")


class Completions:
    def __init__(self, times=1):
        self.times = times

    def create(self, **kwargs):
        return iterable(self.times)


class Chat:
    def __init__(self, times=1, is_async=False):
        if is_async is True:
            self.completions = ACompletions(times=times)
        else:
            self.completions = Completions(times=times)


class MockSyncOpenAI:
    def __init__(self, api_key=None, times=1):
        self.chat = Chat(times=times, is_async=False)


def handle_log(_event, _data):
    pass


def describe_cast_to_input():
    def test_it_casts_to_parsed_input():
        with patch("diagraph.llm.openai_llm.openai_llm.SyncOpenAI", MockSyncOpenAI):
            from .openai_llm import cast_to_input

            assert cast_to_input("foo") == (
                [{"role": "user", "content": "foo"}],
                {},
            )

    def test_it_returns_if_not_a_string():
        with patch("diagraph.llm.openai_llm.openai_llm.SyncOpenAI", MockSyncOpenAI):
            from .openai_llm import cast_to_input

            input = [{"role": "user", "content": "foo"}]
            assert cast_to_input(
                {
                    "messages": input,
                },
            ) == (input, {})

    def test_it_returns_extra_kwargs():
        with patch("diagraph.llm.openai_llm.openai_llm.SyncOpenAI", MockSyncOpenAI):
            from .openai_llm import cast_to_input

            input = [{"role": "user", "content": "foo"}]
            kwargs = {
                "foo": "foo",
            }
            assert cast_to_input({"messages": input, **kwargs}) == (
                input,
                kwargs,
            )
