import pytest

from diagraph import LLM, Diagraph, prompt


@pytest.fixture(autouse=True)
def _clear_defaults(request):
    Diagraph.set_error(None)
    Diagraph.set_llm(None)
    Diagraph.set_log(None)
    yield
    Diagraph.set_error(None)
    Diagraph.set_llm(None)
    Diagraph.set_log(None)


def describe_llm():
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

    def test_it_sets_a_function_llm(mocker):
        log = mocker.stub()

        times = 3

        @prompt(llm=MockLLM(times=times))
        def fn():
            return "test prompt"

        Diagraph(fn, log=log).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None, fn)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i, fn)
        log.assert_any_call("end", None, fn)

    def test_it_sets_a_default_llm(mocker):
        log = mocker.stub()

        times = 3

        Diagraph.set_llm(MockLLM(times=times))

        @prompt()
        def fn():
            return "test prompt"

        Diagraph(fn, log=log).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None, fn)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i, fn)
        log.assert_any_call("end", None, fn)

    def test_it_sets_a_diagraph_llm(mocker):
        log = mocker.stub()

        times = 3

        @prompt()
        def fn():
            return "test prompt"

        Diagraph(fn, log=log, llm=MockLLM(times=times)).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None, fn)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i, fn)
        log.assert_any_call("end", None, fn)

    def test_it_overrides_a_default_llm(mocker):
        log = mocker.stub()

        times = 3

        Diagraph.set_llm(MockLLM(times=0))

        @prompt(llm=MockLLM(times=times))
        def fn():
            return "test prompt"

        Diagraph(fn, log=log).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None, fn)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i, fn)
        log.assert_any_call("end", None, fn)

    def test_it_overrides_a_diagraph_llm(mocker):
        log = mocker.stub()

        times = 3

        @prompt(llm=MockLLM(times=times))
        def fn():
            return "test prompt"

        Diagraph(fn, log=log, llm=MockLLM(times=0)).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None, fn)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i, fn)
        log.assert_any_call("end", None, fn)

    def test_it_overrides_a_diagraph_and_global_llm(mocker):
        log = mocker.stub()

        times = 3

        Diagraph.set_llm(MockLLM(times=0))

        @prompt(llm=MockLLM(times=times))
        def fn():
            return "test prompt"

        Diagraph(fn, log=log, llm=MockLLM(times=0)).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None, fn)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i, fn)
        log.assert_any_call("end", None, fn)

    def test_it_overrides_a_global_llm_from_a_diagraph_llm(mocker):
        log = mocker.stub()

        times = 3

        Diagraph.set_llm(MockLLM(times=0))

        @prompt()
        def fn():
            return "test prompt"

        Diagraph(fn, log=log, llm=MockLLM(times=times)).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None, fn)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i, fn)
        log.assert_any_call("end", None, fn)
