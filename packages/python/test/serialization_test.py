import pickle
from collections.abc import Callable
from inspect import getsource as _getsource
from textwrap import dedent
from typing import Any
from unittest.mock import ANY, mock_open, patch

import pytest

from diagraph import LLM, Depends, Diagraph, OpenAI, prompt


def getsource(fn: Callable):
    return dedent(_getsource(fn)).strip()


def describe_serialization():
    def describe_from_json():
        @pytest.mark.parametrize(
            "version",
            [
                ("foo",),
                (None,),
                (999,),
            ],
        )
        def test_it_raises_on_an_unsupported_version(version):
            with pytest.raises(Exception, match="Unsupported version"):
                Diagraph.from_json(
                    {
                        "version": version,
                    },
                )

        def describe_version_1():
            def test_it_deserializes_a_one_node_diagraph():
                def foo():
                    return "foo"

                dg = Diagraph.from_json(
                    {
                        "version": "1",
                        "nodes": {
                            "foo": {
                                "inputs": [],
                                "fn": getsource(foo),
                                "is_terminal": True,
                            },
                        },
                    },
                )
                assert dg["foo"].fn() == "foo"
                assert dg.run().result == "foo"

            def test_it_raises_appropriately_if_not_using_string_keys():
                def foo():
                    return "foo"

                dg = Diagraph.from_json(
                    {
                        "version": "1",
                        "nodes": {
                            "foo": {
                                "inputs": [],
                                "fn": getsource(foo),
                                "is_terminal": True,
                            },
                        },
                    },
                )
                with pytest.raises(
                    Exception,
                    match="This Diagraph was created from JSON",
                ):
                    dg[foo].fn()

            def test_it_deserializes_a_one_node_diagraph_with_args():
                def foo(arg):
                    return f"foo: {arg}"

                dg = Diagraph.from_json(
                    {
                        "version": "1",
                        "nodes": {
                            "foo": {
                                "inputs": [],
                                "fn": getsource(foo),
                                "is_terminal": True,
                            },
                        },
                    },
                )
                assert dg["foo"].fn("a") == "foo: a"
                assert dg.run("b").result == "foo: b"

            def test_it_deserializes_a_one_node_diagraph_with_args_and_types():
                def foo(arg: str):
                    return f"foo: {arg}"

                dg = Diagraph.from_json(
                    {
                        "version": "1",
                        "nodes": {
                            "foo": {
                                "inputs": [],
                                "is_terminal": True,
                                "fn": getsource(foo),
                            },
                        },
                    },
                )
                assert dg["foo"].fn("a") == "foo: a"
                assert dg.run("b").result == "foo: b"

            def test_it_deserializes_a_diagraph_with_dependencies():
                def foo():
                    return "foo"

                def bar(foo1=Depends("foo")):
                    return f"bar{foo1}"

                dg = Diagraph.from_json(
                    {
                        "version": "1",
                        "nodes": {
                            "foo": {
                                "inputs": [],
                                "fn": getsource(foo),
                            },
                            "bar": {
                                "inputs": [
                                    "foo",
                                ],
                                "fn": getsource(bar),
                                "is_terminal": True,
                            },
                        },
                    },
                )
                assert dg["foo"].fn() == "foo"
                assert dg["bar"].fn("foo1") == "barfoo1"
                assert dg.run().result == "barfoo"

            def test_it_deserializes_a_diagraph_with_prompt(mocker):
                stub = mocker.stub()

                def fake_run(self, string, stream=None, **kwargs):
                    stub(string)
                    return string + "_"

                with patch.object(
                    OpenAI,
                    "run",
                    fake_run,
                ):

                    @prompt
                    def foo():
                        return "foo"

                    dg = Diagraph.from_json(
                        {
                            "version": "1",
                            "nodes": {
                                "foo": {
                                    "inputs": [],
                                    "fn": getsource(foo),
                                    "is_terminal": True,
                                },
                            },
                        },
                    )
                    assert dg.run().result == "foo_"
                assert stub.call_count == 1
                stub.assert_any_call("foo")

            def test_it_deserializes_a_diagraph_with_prompt_fn(mocker):
                stub = mocker.stub()

                def fake_run(self, string, stream=None, **kwargs):
                    stub(string)
                    return string + "_"

                with patch.object(
                    OpenAI,
                    "run",
                    fake_run,
                ):

                    @prompt()
                    def foo():
                        return "foo"

                    dg = Diagraph.from_json(
                        {
                            "version": "1",
                            "nodes": {
                                "foo": {
                                    "inputs": [],
                                    "fn": getsource(foo),
                                    "is_terminal": True,
                                },
                            },
                        },
                    )
                    assert dg.run().result == "foo_"
                assert stub.call_count == 1
                stub.assert_any_call("foo")

            def test_it_deserializes_a_diagraph_with_builtin_llm(mocker):
                stub = mocker.stub()

                def fake_run(self, string, stream=None, **kwargs):
                    stub(string, **self.kwargs)
                    return string + "_"

                with patch.object(
                    OpenAI,
                    "run",
                    fake_run,
                ):

                    @prompt(llm=OpenAI(model="gpt-foo"))
                    def foo():
                        return "foo"

                    dg = Diagraph.from_json(
                        {
                            "version": "1",
                            "nodes": {
                                "foo": {
                                    "inputs": [],
                                    "fn": getsource(foo),
                                    "is_terminal": True,
                                },
                            },
                        },
                    )
                    assert dg.run().result == "foo_"
                assert stub.call_count == 1
                stub.assert_any_call("foo", model="gpt-foo")

            def test_it_deserializes_a_diagraph_with_custom_llm_defined_locally(
                mocker,
            ):
                stub = mocker.stub()

                class MockLLM(LLM):
                    def run(self, prompt, log, model=None, stream=None, **kwargs):
                        stub(prompt)
                        return f"{prompt}__"

                llm = MockLLM()

                @prompt(llm=llm)
                def foo():
                    return "foo"

                dg = Diagraph.from_json(
                    {
                        "version": "1",
                        "nodes": {
                            "foo": {
                                "inputs": [],
                                "fn": getsource(foo),
                                "is_terminal": True,
                                "args": {
                                    "llm": llm,
                                },
                            },
                        },
                    },
                )
                assert dg.run().result == "foo__"
                assert stub.call_count == 1
                stub.assert_any_call("foo")

            def test_it_deserializes_a_diagraph_with_custom_error_handler_defined_locally(
                mocker,
            ):
                stub = mocker.stub()
                e = Exception("test error")

                def fake_run(self, string, stream=None, **kwargs):
                    raise e

                with patch.object(
                    OpenAI,
                    "run",
                    fake_run,
                ):

                    def error_handler(e: Exception, r: Any) -> str:
                        stub(e)
                        return "errored"

                    @prompt(error=error_handler)
                    def foo():
                        return "foo"

                    dg = Diagraph.from_json(
                        {
                            "version": "1",
                            "nodes": {
                                "foo": {
                                    "inputs": [],
                                    "fn": getsource(foo),
                                    "is_terminal": True,
                                    "args": {
                                        "error_handler": error_handler,
                                    },
                                },
                            },
                        },
                    )
                    assert dg.run().result == "errored"
                    assert stub.call_count == 1
                    stub.assert_any_call(e)

            def test_it_deserializes_a_diagraph_with_custom_log_handler_defined_locally(
                mocker,
            ):
                stub = mocker.stub()

                def fake_run(self, string, log, stream=None, **kwargs):
                    log("start", None)
                    log("data", string)
                    log("end", None)
                    return string + "_"

                with patch.object(
                    OpenAI,
                    "run",
                    fake_run,
                ):

                    def log_handler(*args, **kwargs):
                        stub(*args, **kwargs)

                    @prompt(log=log_handler)
                    def foo():
                        return "foo"

                    dg = Diagraph.from_json(
                        {
                            "version": "1",
                            "nodes": {
                                "foo": {
                                    "inputs": [],
                                    "fn": getsource(foo),
                                    "is_terminal": True,
                                    "args": {
                                        "log_handler": log_handler,
                                    },
                                },
                            },
                        },
                    )
                    assert dg.run("foo").result == "foo_"
                    assert stub.call_count == 3
                    stub.assert_any_call("start", None)
                    stub.assert_any_call("data", "foo")
                    stub.assert_any_call("end", None)

            def test_it_deserializes_a_diagraph_with_custom_code_defined_locally(
                mocker,
            ):
                log_stub = mocker.stub()
                error_stub = mocker.stub()
                llm_stub = mocker.stub()

                e = Exception("test error")

                class MockLLM(LLM):
                    def run(self, prompt, log, model=None, stream=None, **kwargs):
                        llm_stub(prompt)
                        log("start", None)
                        log("data", prompt)
                        log("end", None)
                        raise e

                llm = MockLLM()

                def error_handler(e: Exception, r: Any) -> str:
                    error_stub(e)
                    return "errored"

                def log_handler(*args, **kwargs):
                    log_stub(*args, **kwargs)

                @prompt(llm=llm, error=error_handler, log=log_handler)
                def foo():
                    return "foo"

                dg = Diagraph.from_json(
                    {
                        "version": "1",
                        "nodes": {
                            "foo": {
                                "inputs": [],
                                "fn": getsource(foo),
                                "is_terminal": True,
                                "args": {
                                    "llm": llm,
                                    "error_handler": error_handler,
                                    "log_handler": log_handler,
                                },
                            },
                        },
                    },
                )
                assert dg.run("foo").result == "errored"
                assert log_stub.call_count == 3
                log_stub.assert_any_call("start", None)
                log_stub.assert_any_call("data", "foo")
                log_stub.assert_any_call("end", None)
                assert error_stub.call_count == 1
                error_stub.assert_any_call(e)
                assert llm_stub.call_count == 1
                llm_stub.assert_any_call("foo")

            def test_it_deserializes_a_diagraph_with_custom_code_defined_globally(
                mocker,
            ):
                log_stub = mocker.stub()
                error_stub = mocker.stub()
                llm_stub = mocker.stub()

                e = Exception("test error")

                class MockLLM(LLM):
                    def run(self, prompt, log, model=None, stream=None, **kwargs):
                        llm_stub(prompt)
                        log("start", None)
                        log("data", prompt)
                        log("end", None)
                        raise e

                llm = MockLLM()

                def error_handler(e: Exception, r: Any, fn) -> str:
                    error_stub(e)
                    return "errored"

                def log_handler(event, chunk, _fn):
                    log_stub(event, chunk)

                @prompt
                def foo():
                    return "foo"

                dg = Diagraph.from_json(
                    {
                        "version": "1",
                        "nodes": {
                            "foo": {
                                "inputs": [],
                                "fn": getsource(foo),
                                "is_terminal": True,
                            },
                        },
                        "args": {
                            "llm": llm,
                            "error": error_handler,
                            "log": log_handler,
                        },
                    },
                )
                assert dg.run("foo").result == "errored"
                assert log_stub.call_count == 3
                log_stub.assert_any_call("start", None)
                log_stub.assert_any_call("data", "foo")
                log_stub.assert_any_call("end", None)
                assert error_stub.call_count == 1
                error_stub.assert_any_call(e)
                assert llm_stub.call_count == 1
                llm_stub.assert_any_call("foo")

    def describe_to_json():
        def describe_version_1():
            @pytest.mark.parametrize(
                "version",
                [
                    ("foo",),
                    (None,),
                    (999,),
                ],
            )
            def test_it_raises_on_an_unsupported_version(version):
                with pytest.raises(Exception, match="Unsupported version"):
                    Diagraph().to_json(version=version)

            def test_it_serializes_a_one_node_diagraph():
                def foo():
                    return "foo"

                dg = Diagraph(foo)

                assert dg.to_json() == {
                    "version": "1",
                    "nodes": {
                        "foo": {
                            "fn": getsource(foo),
                            "is_terminal": True,
                        },
                    },
                }

            def test_it_serializes_a_one_node_diagraph_with_args():
                def foo(arg):
                    return f"foo: {arg}"

                dg = Diagraph(foo)

                config = dg.to_json()
                assert config == {
                    "version": "1",
                    "nodes": {
                        "foo": {
                            "fn": getsource(foo),
                            "is_terminal": True,
                        },
                    },
                }
                dg2 = Diagraph.from_json(config)
                assert dg2["foo"].fn("a") == "foo: a"
                assert dg2.run("b").result == "foo: b"

            def test_it_serializes_a_one_node_diagraph_with_args_and_types():
                def foo(arg):
                    return f"foo: {arg}"

                dg = Diagraph(foo)

                config = dg.to_json()

                assert config == {
                    "version": "1",
                    "nodes": {
                        "foo": {
                            "fn": getsource(foo),
                            "is_terminal": True,
                        },
                    },
                }
                dg2 = Diagraph.from_json(config)
                assert dg2["foo"].fn("a") == "foo: a"
                assert dg2.run("b").result == "foo: b"

            def test_it_serializes_a_diagraph_with_fn_dependencies():
                def foo():
                    return "foo"

                def bar(foo1=Depends(foo)):
                    return f"bar{foo1}"

                dg = Diagraph(bar)

                config = dg.to_json()

                assert config == {
                    "version": "1",
                    "nodes": {
                        "foo": {
                            "fn": getsource(foo),
                        },
                        "bar": {
                            "inputs": ["foo"],
                            "fn": 'def bar(foo1=Depends("foo")):\n    return f"bar{foo1}"',
                            "is_terminal": True,
                        },
                    },
                }

                dg2 = Diagraph.from_json(config)
                assert dg2["foo"].fn() == "foo"
                assert dg2["bar"].fn("foo1") == "barfoo1"
                assert dg2.run().result == "barfoo"

            def test_it_serializes_a_diagraph_with_string_dependencies():
                def foo():
                    return "foo"

                def bar(foo1=Depends("foo")):
                    return f"bar{foo1}"

                dg = Diagraph(
                    bar,
                    node_dict={"foo": foo, "bar": bar},
                    use_string_keys=True,
                )

                config = dg.to_json()

                assert config == {
                    "version": "1",
                    "nodes": {
                        "foo": {
                            "fn": getsource(foo),
                        },
                        "bar": {
                            "inputs": ["foo"],
                            "fn": 'def bar(foo1=Depends("foo")):\n    return f"bar{foo1}"',
                            "is_terminal": True,
                        },
                    },
                }

                dg2 = Diagraph.from_json(config)
                assert dg2["foo"].fn() == "foo"
                assert dg2["bar"].fn("foo1") == "barfoo1"
                assert dg2.run().result == "barfoo"

            def test_it_serializes_a_diagraph_with_prompt(mocker):
                stub = mocker.stub()

                def fake_run(self, string, stream=None, **kwargs):
                    stub(string)
                    return string + "_"

                with patch.object(
                    OpenAI,
                    "run",
                    fake_run,
                ):

                    @prompt
                    def foo():
                        return "foo"

                    dg = Diagraph(foo)

                    config = dg.to_json()

                    assert config == {
                        "version": "1",
                        "nodes": {
                            "foo": {
                                "fn": getsource(foo),
                                "is_terminal": True,
                            },
                        },
                    }

            def test_it_serializes_a_diagraph_with_prompt_fn(mocker):
                stub = mocker.stub()

                def fake_run(self, string, stream=None, **kwargs):
                    stub(string)
                    return string + "_"

                with patch.object(
                    OpenAI,
                    "run",
                    fake_run,
                ):

                    @prompt()
                    def foo():
                        return "foo"

                    dg = Diagraph(foo)

                    config = dg.to_json()

                    assert config == {
                        "version": "1",
                        "nodes": {
                            "foo": {
                                "fn": getsource(foo),
                                "is_terminal": True,
                            },
                        },
                    }

            def test_it_serializes_a_diagraph_with_builtin_llm(mocker):
                stub = mocker.stub()

                def fake_run(self, string, stream=None, **kwargs):
                    stub(string, **self.kwargs)
                    return string + "_"

                with patch.object(
                    OpenAI,
                    "run",
                    fake_run,
                ):

                    @prompt(llm=OpenAI(model="gpt-foo"))
                    def foo():
                        return "foo"

                    dg = Diagraph(foo)

                    config = dg.to_json()

                    assert config == {
                        "version": "1",
                        "nodes": {
                            "foo": {
                                "fn": getsource(foo),
                                "is_terminal": True,
                            },
                        },
                    }

            def test_it_serializes_a_diagraph_with_custom_llm_defined_locally(
                mocker,
            ):
                stub = mocker.stub()

                class MockLLM(LLM):
                    def run(self, prompt, log, model=None, stream=None, **kwargs):
                        stub(prompt)
                        return f"{prompt}__"

                llm = MockLLM()

                @prompt(llm=llm)
                def foo():
                    return "foo"

                dg = Diagraph(foo)

                config = dg.to_json()

                assert config == {
                    "version": "1",
                    "nodes": {
                        "foo": {
                            "fn": getsource(foo),
                            "is_terminal": True,
                        },
                    },
                }

            def test_it_serializes_a_diagraph_with_custom_error_handler_defined_locally(
                mocker,
            ):
                stub = mocker.stub()
                e = Exception("test error")

                def fake_run(self, string, stream=None, **kwargs):
                    raise e

                with patch.object(
                    OpenAI,
                    "run",
                    fake_run,
                ):

                    def error_handler(e: Exception, r: Any) -> str:
                        stub(e)
                        return "errored"

                    @prompt(error=error_handler)
                    def foo():
                        return "foo"

                    dg = Diagraph(foo)

                    config = dg.to_json()

                    assert config == {
                        "version": "1",
                        "nodes": {
                            "foo": {
                                "fn": getsource(foo),
                                "is_terminal": True,
                                # "args": {
                                #     "error_handler": error_handler,
                                # },
                            },
                        },
                    }

            def test_it_serializes_a_diagraph_with_custom_log_handler_defined_locally(
                mocker,
            ):
                stub = mocker.stub()

                def fake_run(self, string, log, stream=None, **kwargs):
                    log("start", None)
                    log("data", string)
                    log("end", None)
                    return string + "_"

                with patch.object(
                    OpenAI,
                    "run",
                    fake_run,
                ):

                    def log_handler(*args, **kwargs):
                        stub(*args, **kwargs)

                    @prompt(log=log_handler)
                    def foo():
                        return "foo"

                    dg = Diagraph(foo)

                    config = dg.to_json()

                    assert config == {
                        "version": "1",
                        "nodes": {
                            "foo": {
                                "fn": getsource(foo),
                                "is_terminal": True,
                                # "args": {
                                # "log_handler": log_handler,
                                # },
                            },
                        },
                    }

            def test_it_serializes_a_diagraph_with_custom_code_defined_locally(
                mocker,
            ):
                log_stub = mocker.stub()
                error_stub = mocker.stub()
                llm_stub = mocker.stub()

                e = Exception("test error")

                class MockLLM(LLM):
                    def run(self, prompt, log, model=None, stream=None, **kwargs):
                        llm_stub(prompt)
                        log("start", None)
                        log("data", prompt)
                        log("end", None)
                        raise e

                llm = MockLLM()

                def error_handler(e: Exception, r: Any) -> str:
                    error_stub(e)
                    return "errored"

                def log_handler(*args, **kwargs):
                    log_stub(*args, **kwargs)

                @prompt(llm=llm, error=error_handler, log=log_handler)
                def foo():
                    return "foo"

                dg = Diagraph(foo)

                config = dg.to_json()

                assert config == {
                    "version": "1",
                    "nodes": {
                        "foo": {
                            "fn": getsource(foo),
                            "is_terminal": True,
                            # "args": {
                            # "llm": llm,
                            # "error_handler": error_handler,
                            # "log_handler": log_handler,
                            # },
                        },
                    },
                }

            def test_it_serializes_a_diagraph_with_custom_code_defined_globally(
                mocker,
            ):
                log_stub = mocker.stub()
                error_stub = mocker.stub()
                llm_stub = mocker.stub()

                e = Exception("test error")

                class MockLLM(LLM):
                    def run(self, prompt, log, model=None, stream=None, **kwargs):
                        llm_stub(prompt)
                        log("start", None)
                        log("data", prompt)
                        log("end", None)
                        raise e

                llm = MockLLM()

                def error_handler(e: Exception, r: Any, fn) -> str:
                    error_stub(e)
                    return "errored"

                def log_handler(event, chunk, _fn):
                    log_stub(event, chunk)

                @prompt
                def foo():
                    return "foo"

                dg = Diagraph(foo, llm=llm, error=error_handler, log=log_handler)

                config = dg.to_json()

                assert config == {
                    "version": "1",
                    "nodes": {
                        "foo": {
                            "fn": getsource(foo),
                            "is_terminal": True,
                        },
                    },
                    # "args": {
                    #     "llm": llm,
                    #     "error": error_handler,
                    #     "log": log_handler,
                    # },
                }


def describe_saving_and_loading():
    @pytest.mark.parametrize(
        ("filepath", "mode"),
        [
            ("foo", "wb"),
            ("foo.foo", "wb"),
            ("foo.json", "w"),
        ],
    )
    def test_it_saves(filepath, mode):
        with patch("pathlib.Path.open", mock_open()) as mock_file_handle, patch(
            "pickle.dumps",
        ) as mock_pickle_dump, patch("json.dump") as mock_json_dump:

            def fn():
                ...

            dg = Diagraph(fn)

            dg.save(filepath)

            mock_file_handle.assert_called_once_with(mode)

            if mode == "wb":
                mock_pickle_dump.assert_called_once_with(ANY)
            else:
                mock_json_dump.assert_called_once_with(ANY, ANY)

    @pytest.mark.parametrize(
        ("filepath", "filetype"),
        [
            ("foo", "pickle"),
            ("foo", "json"),
            ("foo.foo", "pickle"),
            ("foo.foo", "json"),
            ("foo.json", "pickle"),
            ("foo.json", "json"),
        ],
    )
    def test_it_saves_with_specific_filetype(filepath, filetype):
        with patch("pathlib.Path.open", mock_open()) as _mock_file_handle, patch(
            "pickle.dumps",
        ) as mock_pickle_dump, patch("json.dump") as mock_json_dump:

            def fn():
                ...

            dg = Diagraph(fn)

            dg.save(filepath, filetype)

            if filetype == "pickle":
                mock_pickle_dump.assert_called_once_with(ANY)
            else:
                mock_json_dump.assert_called_once_with(ANY, ANY)

    @pytest.mark.parametrize(
        ("filepath", "filetype"),
        [
            # ("foo", "pickle"), ("foo.pkl", "pickle"),
            ("bar", "json"),
            ("bar.json", None),
            ("bar.json", "json"),
        ],
    )
    def test_it_loads_from_json(filepath, filetype):
        with patch(
            "pathlib.Path.open",
            mock_open(read_data='{ "nodes": []}'),
        ) as mock_path_open, patch("json.load") as mock_json_load:
            # Call the function under test

            mock_json_load.return_value = {
                "version": "1",
                "nodes": {
                    "foo": {
                        "fn": "def foo():\n    return 'foo'",
                        "is_terminal": True,
                    },
                },
            }
            Diagraph.load(filepath, filetype)

            mock_path_open.assert_called_once_with("r")
            mock_json_load.assert_called_once()

    @pytest.mark.parametrize(
        ("filepath", "filetype"),
        [
            ("bar", None),
            ("bar", "pickle"),
            ("bar.pkl", None),
            ("bar.pkl", "pickle"),
            ("bar.json", "pickle"),
        ],
    )
    def test_it_loads_from_pickle(filepath, filetype):
        with patch(
            "pathlib.Path.open",
            mock_open(read_data='{ "nodes": []}'),
        ) as mock_path_open, patch("json.loads") as mock_json_load:
            # Call the function under test

            # Setup the return value for pathlib.Path.open
            mock_file_handle = mock_open().return_value
            config = {
                "version": "1",
                "nodes": {
                    "foo": {
                        "fn": "def foo():\n    return 'foo'",
                        "is_terminal": True,
                    },
                },
            }
            pickled_content = pickle.dumps(config)
            mock_file_handle.read.return_value = pickled_content
            mock_path_open.return_value = mock_file_handle
            mock_json_load.return_value = config

            # Setup the return value for pickle.load
            Diagraph.load(filepath, filetype)

            mock_path_open.assert_called_once_with("rb")

            mock_json_load.assert_called_once_with(config)
