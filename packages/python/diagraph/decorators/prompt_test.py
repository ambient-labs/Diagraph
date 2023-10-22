import pytest

from ..classes.diagraph import Diagraph
from ..llm.llm import LLM
from ..utils.depends import Depends
from .prompt import prompt


class MockLLM(LLM):
    times: int
    error: bool | int
    error_times = 0

    def __init__(self, times=0, error: bool | int = False, **kwargs):
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
        if self.error is True:
            raise Exception("test error")
        if isinstance(self.error, int) and self.error_times < self.error:
            error_times = self.error_times
            self.error_times += 1
            print(f"test error: {error_times}")
            raise Exception(f"test error: {error_times}")
        log("start", None)

        for i in range(self.times):
            i = f"{i}"
            response += i
            log("data", i)
        log("end", None)
        return response


def describe_logs():
    def test_it_handles_logs_for_a_diagraph(mocker):
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

    def test_it_can_set_a_default_log(mocker):
        log = mocker.stub()

        times = 3

        Diagraph.set_log(log)

        @prompt(llm=MockLLM(times=times))
        def fn():
            return "test prompt"

        Diagraph(fn).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None, fn)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i, fn)
        log.assert_any_call("end", None, fn)

    def test_a_default_log_fn_can_be_overridden_at_the_diagraph_level(mocker):
        default_log = mocker.stub()
        log = mocker.stub()

        times = 3

        Diagraph.set_log(default_log)

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
        assert default_log.call_count == 0

    def test_it_handles_logs_for_a_fn(mocker):
        log = mocker.stub()

        times = 3

        @prompt(llm=MockLLM(times=times), log=log)
        def fn():
            return "test prompt"

        Diagraph(fn).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i)
        log.assert_any_call("end", None)

    def test_a_diagraph_log_fn_can_be_overridden_at_the_function_level(mocker):
        diagraph_log = mocker.stub()
        log = mocker.stub()

        times = 3

        @prompt(llm=MockLLM(times=times), log=log)
        def fn():
            return "test prompt"

        Diagraph(fn, log=diagraph_log).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i)
        log.assert_any_call("end", None)
        assert diagraph_log.call_count == 0

    def test_a_global_log_fn_can_be_overridden_at_the_function_level(mocker):
        global_log = mocker.stub()
        log = mocker.stub()

        times = 3

        Diagraph.set_log(global_log)

        @prompt(llm=MockLLM(times=times), log=log)
        def fn():
            return "test prompt"

        Diagraph(fn).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i)
        log.assert_any_call("end", None)
        assert global_log.call_count == 0

    def test_a_global_and_diagraph_log_fn_can_be_overridden_at_the_function_level(
        mocker,
    ):
        global_log = mocker.stub()
        diagraph_log = mocker.stub()
        log = mocker.stub()

        times = 3

        Diagraph.set_log(global_log)

        @prompt(llm=MockLLM(times=times), log=log)
        def fn():
            return "test prompt"

        Diagraph(fn, log=diagraph_log).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i)
        log.assert_any_call("end", None)
        assert global_log.call_count == 0
        assert diagraph_log.call_count == 0


def describe_errors():
    def test_it_saves_exception_on_the_node(mocker):
        handle_errors = mocker.stub()
        thrown_exception = Exception("test error")
        handle_errors.side_effect = thrown_exception

        @prompt(llm=MockLLM(error=True), error=handle_errors)
        def fn():
            return "prompt"

        with pytest.raises(Exception, match="Errors encountered"):
            dg = Diagraph(fn).run()
            assert handle_errors.call_count == 1
            assert dg[fn].error == thrown_exception
            assert dg[fn].result is None

    def test_it_saves_subsequent_exceptions_on_the_node(mocker):
        handle_errors = mocker.stub()
        thrown_exception_one = Exception("one")
        handle_errors.side_effect = thrown_exception_one

        @prompt(llm=MockLLM(error=True), error=handle_errors)
        def fn():
            return "prompt"

        dg = Diagraph(fn)
        with pytest.raises(Exception, match="Errors encountered"):
            dg.run()
            assert handle_errors.call_count == 1
            assert dg[fn].error == thrown_exception_one

        thrown_exception_two = Exception("two")
        handle_errors.side_effect = thrown_exception_two
        with pytest.raises(Exception, match="Errors encountered"):
            dg.run()
            assert handle_errors.call_count == 2
            assert dg[fn].error == thrown_exception_two
            assert dg[fn].result is None

    def test_it_saves_multiple_exceptions(mocker):
        handle_errors_a = mocker.stub()
        thrown_exception_a = Exception("a")
        handle_errors_a.side_effect = thrown_exception_a

        handle_errors_b = mocker.stub()
        thrown_exception_b = Exception("b")
        handle_errors_b.side_effect = thrown_exception_b

        @prompt(llm=MockLLM(error=True), error=handle_errors_a)
        def a():
            return "prompt"

        @prompt(llm=MockLLM(error=True), error=handle_errors_b)
        def b():
            return "prompt"

        with pytest.raises(Exception, match="Errors encountered"):
            dg = Diagraph(a, b).run()
            assert handle_errors_a.call_count == 1
            assert handle_errors_b.call_count == 1
            assert dg[a].error == thrown_exception_a
            assert dg[b].error == thrown_exception_b

    def test_it_does_not_run_dependent_function_of_errored_function(mocker):
        handle_errors_a = mocker.stub()
        thrown_exception_a = Exception("a")
        handle_errors_a.side_effect = thrown_exception_a

        @prompt(llm=MockLLM(error=True), error=handle_errors_a)
        def a():
            return "a"

        mock_b = mocker.stub()
        mock_b.return_value = "b"

        @prompt(llm=MockLLM())
        def b(a=Depends(a)):
            return mock_b()

        with pytest.raises(Exception, match="Errors encountered"):
            dg = Diagraph(b).run()
            assert handle_errors_a.call_count == 1
            assert dg[a].error == thrown_exception_a
            assert mock_b.call_count == 0

    def test_it_does_not_run_grand_dependent_function_of_errored_function(mocker):
        handle_errors_a = mocker.stub()
        thrown_exception_a = Exception("a")
        handle_errors_a.side_effect = thrown_exception_a

        @prompt(llm=MockLLM(error=True), error=handle_errors_a)
        def a():
            return "a"

        mock_b = mocker.stub()
        mock_b.return_value = "b"

        @prompt(llm=MockLLM(error=True))
        def b(a=Depends(a)):
            return mock_b()

        mock_c = mocker.stub()
        mock_c.return_value = "c"

        @prompt(llm=MockLLM())
        def c(b=Depends(b)):
            return mock_c()

        with pytest.raises(Exception, match="Errors encountered"):
            dg = Diagraph(c).run()
            assert handle_errors_a.call_count == 1
            assert dg[a].error == thrown_exception_a
            assert mock_b.call_count == 0
            assert mock_c.call_count == 0

    def test_it_does_not_run_dependent_function_of_multiple_errored_functions(mocker):
        handle_errors_a = mocker.stub()
        thrown_exception_a = Exception("a")
        handle_errors_a.side_effect = thrown_exception_a

        @prompt(llm=MockLLM(error=True), error=handle_errors_a)
        def a():
            return "a"

        handle_errors_b = mocker.stub()
        thrown_exception_b = Exception("b")
        handle_errors_b.side_effect = thrown_exception_b

        @prompt(llm=MockLLM(error=True), error=handle_errors_b)
        def b():
            return "b"

        mock_c = mocker.stub()
        mock_c.return_value = "c"

        @prompt(llm=MockLLM())
        def c(a=Depends(a), b=Depends(b)):
            return mock_c()

        with pytest.raises(Exception, match="Errors encountered"):
            dg = Diagraph(c).run()
            assert handle_errors_a.call_count == 1
            assert dg[a].error == thrown_exception_a
            assert dg[b].error == thrown_exception_b
            assert dg[c].error is None
            assert mock_c.call_count == 0

    def test_it_does_not_run_dependent_function_of_single_errored_functions(mocker):
        handle_errors_a = mocker.stub()
        thrown_exception_a = Exception("a")
        handle_errors_a.side_effect = thrown_exception_a

        @prompt(llm=MockLLM(error=True), error=handle_errors_a)
        def a():
            return "a"

        @prompt(llm=MockLLM(times=3))
        def b():
            return "b"

        mock_c = mocker.stub()
        mock_c.return_value = "c"

        @prompt(llm=MockLLM())
        def c(a=Depends(a), b=Depends(b)):
            return mock_c()

        with pytest.raises(Exception, match="Errors encountered"):
            dg = Diagraph(c).run()
            assert handle_errors_a.call_count == 1
            assert dg[a].error == thrown_exception_a
            assert dg[b].result == "012"
            assert mock_c.call_count == 0

    def test_it_does_run_dependent_function_of_non__errored_functions(mocker):
        handle_errors_a = mocker.stub()
        thrown_exception_a = Exception("a")
        handle_errors_a.side_effect = thrown_exception_a

        @prompt(llm=MockLLM(error=True), error=handle_errors_a)
        def a1():
            return "a1"

        @prompt(llm=MockLLM(times=3))
        def a0():
            return "a0"

        @prompt(llm=MockLLM(times=3))
        def b0(a0=Depends(a0)):
            return "a1"

        mock_c = mocker.stub()
        mock_c.return_value = "c"

        @prompt(llm=MockLLM())
        def c0(a1=Depends(a1), b0=Depends(b0)):
            return mock_c()

        with pytest.raises(Exception, match="Errors encountered"):
            dg = Diagraph(c0).run()
            assert dg[a0].result == "012"
            assert dg[b0].result == "012"
            assert dg[a1].error == thrown_exception_a
            assert mock_c.call_count == 0

    def test_it_does_run_deep_dependent_function_of_non_errored_functions(mocker):
        handle_errors_a = mocker.stub()
        thrown_exception_a = Exception("a")
        handle_errors_a.side_effect = thrown_exception_a

        @prompt(llm=MockLLM(error=True), error=handle_errors_a)
        def a1():
            return "a1"

        mock_b1 = mocker.stub()

        @prompt(llm=MockLLM(times=3))
        def b1(a1=Depends(a1)):
            return mock_b1()

        mock_c1 = mocker.stub()

        @prompt(llm=MockLLM(times=3))
        def c1(b1=Depends(b1)):
            return mock_c1()

        @prompt(llm=MockLLM(times=3))
        def a0():
            return "a0"

        @prompt(llm=MockLLM(times=3))
        def b0(a0=Depends(a0)):
            return "a1"

        @prompt(llm=MockLLM(times=3))
        def c0(b0=Depends(b0)):
            return "c1"

        mock_d = mocker.stub()
        mock_d.return_value = "d"

        @prompt(llm=MockLLM())
        def d0(c1=Depends(c1), c0=Depends(c0)):
            return mock_d()

        with pytest.raises(Exception, match="Errors encountered"):
            dg = Diagraph(d0).run()
            assert dg[a0].result == "012"
            assert dg[b0].result == "012"
            assert dg[c0].result == "012"
            assert dg[a1].error == thrown_exception_a
            assert dg[b1].error is None
            assert dg[c1].error is None
            assert dg[b1].result is None
            assert dg[c1].result is None
            assert mock_b1.call_count == 0
            assert mock_c1.call_count == 0
            assert mock_d.call_count == 0

    def test_it_does_run_deep_dependent_function_of_errored_functions_returning_result(
        mocker,
    ):
        handle_errors_a = mocker.stub()
        handle_errors_a.return_value = "a1"

        @prompt(llm=MockLLM(error=True), error=handle_errors_a)
        def a1():
            return "a1"

        mock_b1 = mocker.stub()

        @prompt(llm=MockLLM(times=3))
        def b1(a1=Depends(a1)):
            return mock_b1()

        mock_c1 = mocker.stub()

        @prompt(llm=MockLLM(times=3))
        def c1(b1=Depends(b1)):
            return mock_c1()

        @prompt(llm=MockLLM(times=3))
        def a0():
            return "a0"

        @prompt(llm=MockLLM(times=3))
        def b0(a0=Depends(a0)):
            return "a1"

        @prompt(llm=MockLLM(times=3))
        def c0(b0=Depends(b0)):
            return "c1"

        mock_d = mocker.stub()
        mock_d.return_value = "d"

        @prompt(llm=MockLLM())
        def d0(c1=Depends(c1), c0=Depends(c0)):
            return mock_d()

        dg = Diagraph(d0).run()
        assert dg[a1].error is None
        assert dg[a1].result == "a1"
        assert mock_b1.call_count == 1
        assert mock_c1.call_count == 1
        assert mock_d.call_count == 1

    def test_it_saves_subsequent_error_results_on_the_node(mocker):
        handle_errors = mocker.stub()
        handle_errors.return_value = "foo"

        @prompt(llm=MockLLM(error=True), error=handle_errors)
        def fn():
            return "prompt"

        dg = Diagraph(fn)
        dg.run()
        assert handle_errors.call_count == 1
        assert dg[fn].error is None
        assert dg[fn].result == "foo"

        handle_errors.return_value = "bar"
        dg.run()
        assert handle_errors.call_count == 2
        assert dg[fn].error is None
        assert dg[fn].result == "bar"

    def test_it_saves_exception_on_the_node_if_error_handler_is_defined_on_diagraph(
        mocker,
    ):
        handle_errors = mocker.stub()
        thrown_exception = Exception("test error")
        handle_errors.side_effect = thrown_exception

        @prompt(llm=MockLLM(error=True))
        def fn():
            return "prompt"

        with pytest.raises(Exception, match="Errors encountered"):
            dg = Diagraph(fn, error=handle_errors).run()
            assert handle_errors.call_count == 1
            assert dg[fn].error == thrown_exception
            assert dg[fn].result is None

    def test_it_saves_exception_on_the_node_if_error_handler_is_defined_globally(
        mocker,
    ):
        handle_errors = mocker.stub()
        thrown_exception = Exception("test error")
        handle_errors.side_effect = thrown_exception

        @prompt(llm=MockLLM(error=True))
        def fn():
            return "prompt"

        Diagraph.set_error(handle_errors)
        with pytest.raises(Exception, match="Errors encountered"):
            dg = Diagraph(fn).run()
            assert handle_errors.call_count == 1
            assert dg[fn].error == thrown_exception
            assert dg[fn].result is None

    def test_a_function_error_handler_takes_precedence_over_a_global_error_handler(
        mocker,
    ):
        global_handle_errors = mocker.stub()
        global_thrown_exception = Exception("global error")
        global_handle_errors.side_effect = global_thrown_exception

        function_handle_errors = mocker.stub()
        function_thrown_exception = Exception("function error")
        function_handle_errors.side_effect = function_thrown_exception

        @prompt(llm=MockLLM(error=True), error=function_handle_errors)
        def fn():
            return "prompt"

        Diagraph.set_error(global_handle_errors)
        with pytest.raises(Exception, match="Errors encountered"):
            dg = Diagraph(fn).run()
            assert global_handle_errors.call_count == 0
            assert function_handle_errors.call_count == 1
            assert dg[fn].error == function_thrown_exception

    def test_a_function_error_handler_takes_precedence_over_a_diagraph_error_handler(
        mocker,
    ):
        diagraph_handle_errors = mocker.stub()
        diagraph_thrown_exception = Exception("diagraph error")
        diagraph_handle_errors.side_effect = diagraph_thrown_exception

        function_handle_errors = mocker.stub()
        function_thrown_exception = Exception("function error")
        function_handle_errors.side_effect = function_thrown_exception

        @prompt(llm=MockLLM(error=True), error=function_handle_errors)
        def fn():
            return "prompt"

        with pytest.raises(Exception, match="Errors encountered"):
            dg = Diagraph(fn, error=diagraph_handle_errors).run()
            assert diagraph_handle_errors.call_count == 0
            assert function_handle_errors.call_count == 1
            assert dg[fn].error == function_thrown_exception

    def test_a_function_error_handler_takes_precedence_over_a_diagraph_and_global_error_handler(
        mocker,
    ):
        diagraph_handle_errors = mocker.stub()
        diagraph_thrown_exception = Exception("diagraph error")
        diagraph_handle_errors.side_effect = diagraph_thrown_exception

        function_handle_errors = mocker.stub()
        function_thrown_exception = Exception("function error")
        function_handle_errors.side_effect = function_thrown_exception

        @prompt(llm=MockLLM(error=True), error=function_handle_errors)
        def fn():
            return "prompt"

        global_handle_errors = mocker.stub()
        global_thrown_exception = Exception("global error")
        global_handle_errors.side_effect = global_thrown_exception

        Diagraph.set_error(global_handle_errors)
        with pytest.raises(Exception, match="Errors encountered"):
            dg = Diagraph(fn, error=diagraph_handle_errors).run()
            assert global_handle_errors.call_count == 0
            assert diagraph_handle_errors.call_count == 0
            assert function_handle_errors.call_count == 1
            assert dg[fn].error == function_thrown_exception

    def test_a_diagraph_error_handler_takes_precedence_over_a_global_error_handler(
        mocker,
    ):
        function_handle_errors = mocker.stub()
        function_thrown_exception = Exception("function error")
        function_handle_errors.side_effect = function_thrown_exception

        @prompt(llm=MockLLM(error=True), error=function_handle_errors)
        def fn():
            return "prompt"

        global_handle_errors = mocker.stub()
        global_thrown_exception = Exception("global error")
        global_handle_errors.side_effect = global_thrown_exception

        Diagraph.set_error(global_handle_errors)
        with pytest.raises(Exception, match="Errors encountered"):
            dg = Diagraph(fn).run()
            assert global_handle_errors.call_count == 0
            assert function_handle_errors.call_count == 1
            assert dg[fn].error == function_thrown_exception

    def test_it_reruns_a_function_that_simulates_a_network_failure(
        mocker,
    ):
        """Simulate that an LLM fails on a network call, and we need to
        repeat it without any modifications so we call rerun again."""
        function_handle_errors = mocker.stub()

        def handle_errors(e, rerun):
            function_handle_errors()
            return rerun()

        @prompt(llm=MockLLM(times=3, error=1), error=handle_errors)
        def fn():
            return "prompt"

        dg = Diagraph(fn).run()
        assert function_handle_errors.call_count == 1
        assert dg.result == "012"

    def test_it_reruns_a_function_defined_on_diagraph_that_simulates_a_network_failure(
        mocker,
    ):
        """Simulate that an LLM fails on a network call, and we need to
        repeat it without any modifications so we call rerun again."""
        function_handle_errors = mocker.stub()

        def handle_errors(e, rerun, fn):
            function_handle_errors()
            return rerun()

        @prompt(llm=MockLLM(times=3, error=1))
        def fn():
            return "prompt"

        dg = Diagraph(fn, error=handle_errors).run()
        assert function_handle_errors.call_count == 1
        assert dg.result == "012"

    def test_it_reruns_a_function_multiple_times(
        mocker,
    ):
        function_handle_errors = mocker.stub()

        def handle_errors(e, rerun):
            function_handle_errors()
            return rerun()

        @prompt(llm=MockLLM(times=3, error=3), error=handle_errors)
        def fn():
            return "prompt"

        dg = Diagraph(fn).run()
        assert function_handle_errors.call_count == 3
        assert dg.result == "012"

    def test_it_reruns_a_function_with_kwargs(
        mocker,
    ):
        function_handle_errors = mocker.stub()

        def handle_errors(e, rerun, times=0):
            function_handle_errors(times)
            return rerun(times=times + 1)

        @prompt(llm=MockLLM(times=3, error=3), error=handle_errors)
        def fn():
            return "prompt"

        dg = Diagraph(fn).run()
        function_handle_errors.assert_any_call(0)
        function_handle_errors.assert_any_call(1)
        function_handle_errors.assert_any_call(2)
        assert dg.result == "012"

    def test_it_reruns_a_function_with_kwargs_and_can_raise(
        mocker,
    ):
        function_handle_errors = mocker.stub()

        def handle_errors(e, rerun, times=0):
            if times > 0:
                raise Exception("stop")
            function_handle_errors(times)
            return rerun(times=times + 1)

        @prompt(llm=MockLLM(times=3, error=3), error=handle_errors)
        def fn():
            return "prompt"

        with pytest.raises(Exception, match="Errors encountered"):
            dg = Diagraph(fn).run()
            function_handle_errors.assert_any_call(0)
            assert dg.result is None
            assert str(dg[fn].error) == "stop"
