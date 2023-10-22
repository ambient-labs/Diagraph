from unittest.mock import Mock, patch

import pytest


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


class MockASyncOpenAI:
    def __init__(self, api_key=None, times=1):
        self.chat = Chat(times=times, is_async=True)


class MockSyncOpenAI:
    def __init__(self, api_key=None, times=1):
        self.chat = Chat(times=times, is_async=False)


def handle_log(_event, _data):
    pass


def describe_openai_llm():
    def test_it_instantiates():
        from .openai_llm import OpenAI

        OpenAI()

    def test_it_runs_foo():
        with patch("diagraph.llm.openai_llm.openai_llm.SyncOpenAI", MockSyncOpenAI):
            from .openai_llm import OpenAI

            assert OpenAI().run("foo", log=handle_log) == "0"

    def test_it_passes_kwargs_and_parses_string_by_default():
        with patch(
            "diagraph.llm.openai_llm.openai_llm.SyncOpenAI",
        ) as mocked_sync_openai:
            fake_create = Mock(return_value=iterable(1))
            mocked_sync_openai.return_value.chat.completions.create = fake_create
            from .openai_llm import DEFAULT_MODEL, OpenAI

            OpenAI().run("foo", log=handle_log, foo="foo")
            fake_create.assert_called_with(
                messages=[{"role": "user", "content": "foo"}],
                model=DEFAULT_MODEL,
                foo="foo",
                stream=True,
            )

    def test_it_accepts_alternate_models():
        with patch(
            "diagraph.llm.openai_llm.openai_llm.SyncOpenAI",
        ) as mocked_sync_openai:
            fake_create = Mock(return_value=iterable(1))
            mocked_sync_openai.return_value.chat.completions.create = fake_create
            from .openai_llm import OpenAI

            OpenAI(model="gpt-foo").run("foo", log=handle_log)
            fake_create.assert_called_with(
                messages=[{"role": "user", "content": "foo"}],
                model="gpt-foo",
                stream=True,
            )

        with patch(
            "diagraph.llm.openai_llm.openai_llm.SyncOpenAI",
        ) as mocked_sync_openai:
            fake_create = Mock(return_value=iterable(1))
            mocked_sync_openai.return_value.chat.completions.create = fake_create
            from .openai_llm import OpenAI

            OpenAI().run("foo", log=handle_log, model="gpt-bar")
            fake_create.assert_called_with(
                messages=[{"role": "user", "content": "foo"}],
                model="gpt-bar",
                stream=True,
            )

        with patch(
            "diagraph.llm.openai_llm.openai_llm.SyncOpenAI",
        ) as mocked_sync_openai:
            fake_create = Mock(return_value=iterable(3))
            mocked_sync_openai.return_value.chat.completions.create = fake_create
            from .openai_llm import OpenAI

            OpenAI(model="gpt-foo").run("foo", log=handle_log, model="gpt-bar")
            fake_create.assert_called_with(
                messages=[{"role": "user", "content": "foo"}],
                model="gpt-bar",
                stream=True,
            )

    def describe_logs():
        def test_it_does_not_call_start_if_encountering_an_error(mocker):
            handle_log = mocker.stub()

            with patch(
                "diagraph.llm.openai_llm.openai_llm.SyncOpenAI",
            ) as mocked_sync_openai:
                fake_create = Mock(return_value=iterable(1))
                mocked_sync_openai.return_value.chat.completions.create = fake_create
                from .openai_llm import OpenAI

                fake_create.side_effect = Exception("wruh wroh")
                with pytest.raises(Exception, match="wruh wroh"):
                    OpenAI(model="gpt-foo").run("foo", log=handle_log)
                assert handle_log.call_count == 0

    def test_it_calls_all_events(mocker):
        handle_log = mocker.stub()

        with patch(
            "diagraph.llm.openai_llm.openai_llm.SyncOpenAI",
        ) as mocked_sync_openai:
            fake_create = Mock(return_value=iterable(3))
            mocked_sync_openai.return_value.chat.completions.create = fake_create
            from .openai_llm import OpenAI

            OpenAI(model="gpt-foo").run("foo", log=handle_log)

            handle_log.assert_any_call("start", None)
            handle_log.assert_any_call("data", {"content": "0"})
            handle_log.assert_any_call("data", {"content": "1"})
            handle_log.assert_any_call("data", {"content": "2"})
            handle_log.assert_any_call("end", None)

    def test_it_returns_content_response(mocker):
        handle_log = mocker.stub()

        with patch(
            "diagraph.llm.openai_llm.openai_llm.SyncOpenAI",
        ) as mocked_sync_openai:
            fake_create = Mock(return_value=iterable(3))
            mocked_sync_openai.return_value.chat.completions.create = fake_create
            from .openai_llm import OpenAI

            assert OpenAI(model="gpt-foo").run("foo", log=handle_log) == "012"


# # except openai.error.Timeout as e:
# #   # Handle timeout error, e.g. retry or log
# #   print(f"OpenAI API request timed out: {e}")
# #   pass
# # except openai.error.APIError as e:
# #   # Handle API error, e.g. retry or log
# #   print(f"OpenAI API returned an API Error: {e}")
# #   pass
# # except openai.error.APIConnectionError as e:
# #   # Handle connection error, e.g. check network or log
# #   print(f"OpenAI API request failed to connect: {e}")
# #   pass
# # except openai.error.InvalidRequestError as e:
# #   # Handle invalid request error, e.g. validate parameters or log
# #   print(f"OpenAI API request was invalid: {e}")
# #   pass
# # except openai.error.AuthenticationError as e:
# #   # Handle authentication error, e.g. check credentials or log
# #   print(f"OpenAI API request was not authorized: {e}")
# #   pass
# # except openai.error.PermissionError as e:
# #   # Handle permission error, e.g. check scope or log
# #   print(f"OpenAI API request was not permitted: {e}")
# #   pass
# # except openai.error.RateLimitError as e:
# #   # Handle rate limit error, e.g. wait or log
# #   print(f"OpenAI API request exceeded rate limit: {e}")
# #   pass
