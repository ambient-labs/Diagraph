from collections.abc import Callable
from inspect import getsource as _getsource
from textwrap import dedent

import pytest

from ...decorators.prompt import prompt
from ...utils.depends import Depends
from .v1 import deserialize


def getsource(fn: Callable):
    return dedent(_getsource(fn))


def describe_v1_deserialize():
    @pytest.mark.parametrize(
        "config",
        [
            {},
            {"nodes": None},
            {"nodes": "foo"},
            {"nodes": []},
            {"nodes": {"foo": "foo"}},
            {"nodes": {"foo": []}},
            {"nodes": {"foo": {}}},
            {
                "nodes": {
                    "foo": {
                        "fn": None,
                    },
                },
            },
            {
                "nodes": {
                    "foo": {
                        "fn": [],
                    },
                },
            },
            {
                "nodes": {
                    "foo": {
                        "fn": "fn",
                    },
                },
            },
            {
                "nodes": {
                    "foo": {
                        "inputs": None,
                    },
                },
            },
            {
                "nodes": {
                    "foo": {
                        "inputs": "foo",
                    },
                },
            },
            {
                "nodes": {
                    "foo": {
                        "inputs": {},
                    },
                },
            },
            {
                "nodes": {
                    "foo": {
                        "inputs": [],
                    },
                },
            },
            {
                "nodes": {
                    "foo": {
                        "inputs": [],
                        "args": "foo",
                    },
                },
            },
            {
                "nodes": {
                    "foo": {
                        "inputs": [],
                        "is_terminal": True,
                    },
                },
                "args": "foo",
            },
            {
                "nodes": {
                    "foo": {
                        "inputs": [],
                        "is_terminal": True,
                    },
                },
                "args": [],
            },
        ],
    )
    def test_it_raises_on_invalid_config(config):
        with pytest.raises(Exception, match="validation error"):
            deserialize(config)

    def test_it_deserializes_a_config():
        def foo():
            return "foo"

        foo_str = getsource(foo)

        config = {
            "nodes": {
                "foo": {
                    "fn": foo_str,
                    "inputs": [],
                    "is_terminal": True,
                },
            },
        }

        result = deserialize(config)
        assert isinstance(result, tuple)
        assert len(result) == 3
        terminal_nodes, node_mapping, _kwargs = result
        assert len(terminal_nodes) == 1
        assert terminal_nodes[0]() == "foo"
        assert isinstance(node_mapping, dict)
        assert node_mapping["foo"]() == "foo"

    def test_it_deserializes_a_config_with_args():
        def foo(arg):
            return f"foo: {arg}"

        foo_str = getsource(foo)

        config = {
            "nodes": {
                "foo": {
                    "fn": foo_str,
                    "inputs": [],
                    "is_terminal": True,
                },
            },
        }

        result = deserialize(config)
        terminal_nodes, node_mapping, kwargs = result
        assert len(terminal_nodes) == 1
        assert terminal_nodes[0]("a") == "foo: a"
        assert isinstance(node_mapping, dict)
        assert node_mapping["foo"]("b") == "foo: b"
        assert kwargs == {}

    def test_it_deserializes_a_config_with_typed_args():
        def foo(arg: str):
            return f"foo: {arg}"

        foo_str = getsource(foo)

        config = {
            "nodes": {
                "foo": {
                    "fn": foo_str,
                    "inputs": [],
                    "is_terminal": True,
                },
            },
        }

        result = deserialize(config)
        terminal_nodes, node_mapping, kwargs = result
        assert len(terminal_nodes) == 1
        assert terminal_nodes[0]("a") == "foo: a"
        assert isinstance(node_mapping, dict)
        assert node_mapping["foo"]("b") == "foo: b"
        assert kwargs == {}

    def test_it_deserializes_a_config_with_dependencies():
        def foo():
            return "foo"

        def bar(foo=Depends("foo")):
            return "bar"

        foo_str = getsource(foo)
        bar_str = getsource(bar)

        config = {
            "nodes": {
                "foo": {
                    "fn": foo_str,
                    "inputs": [],
                },
                "bar": {
                    "fn": bar_str,
                    "inputs": ["foo"],
                    "is_terminal": True,
                },
            },
        }

        result = deserialize(config)
        assert isinstance(result, tuple)
        assert len(result) == 3
        terminal_nodes, node_mapping, kwargs = result
        assert len(terminal_nodes) == 1
        assert terminal_nodes[0]("1") == "bar"
        assert isinstance(node_mapping, dict)
        assert node_mapping["foo"]() == "foo"
        assert node_mapping["bar"]("1") == "bar"
        assert kwargs == {}

    def test_it_deserializes_a_config_with_prompt():
        @prompt
        def foo():
            return "foo"

        foo_str = getsource(foo)

        config = {
            "nodes": {
                "foo": {
                    "fn": foo_str,
                    "inputs": [],
                    "is_terminal": True,
                },
            },
        }

        result = deserialize(config)
        terminal_nodes, node_mapping, kwargs = result
        assert len(terminal_nodes) == 1
        assert isinstance(node_mapping, dict)
        assert kwargs == {}

    def test_it_deserializes_a_config_with_prompt_as_fn():
        @prompt()
        def foo():
            return "foo"

        foo_str = getsource(foo)

        config = {
            "nodes": {
                "foo": {
                    "fn": foo_str,
                    "inputs": [],
                    "is_terminal": True,
                },
            },
        }

        result = deserialize(config)
        terminal_nodes, node_mapping, kwargs = result
        assert len(terminal_nodes) == 1
        assert isinstance(node_mapping, dict)
        assert kwargs == {}

    def test_it_deserializes_a_config_with_global_args():
        @prompt()
        def foo():
            return "foo"

        foo_str = getsource(foo)

        args = {
            "llm": "llm",
            "error": "error",
            "log": "log",
        }

        config = {
            "nodes": {
                "foo": {
                    "fn": foo_str,
                    "inputs": [],
                    "is_terminal": True,
                },
            },
            "args": args,
        }

        result = deserialize(config)
        terminal_nodes, node_mapping, kwargs = result
        assert len(terminal_nodes) == 1
        assert isinstance(node_mapping, dict)
        assert kwargs == args
