import pytest

from .build_dict import build_dict


def describe_build_dict():
    def test_it_builds_a_dict():
        assert build_dict({}, {"a": "b"}) == {"a": "b"}

    def test_it_builds_a_dict_on_existing_dict():
        assert build_dict({"c": "d"}, {"a": "b"}) == {"a": "b", "c": "d"}

    def test_it_appends_an_existing_dict():
        assert build_dict({"a": "d"}, {"a": "b"}) == {"a": "db"}

    def test_it_ignores_a_none():
        assert build_dict({}, {"a": None}) == {}

    def test_it_ignores_a_none_on_existing_dict():
        assert build_dict({"a": "d"}, {"a": None}) == {"a": "d"}

    def test_it_raises_if_encountering_conflicting_types():
        with pytest.raises(Exception, match="Type mismatch"):
            build_dict({"a": "d"}, {"a": {"a": "b"}})

    def test_it_operates_recursively():
        assert build_dict(
            {
                "foo": {"one": "foo"},
                "bar": {"one": "bar"},
            },
            {
                "foo": {
                    "one": "foo1",
                    "two": "foo",
                },
                "bar": {"bar": "bar", "deep": {"one": "bar"}},
                "baz": {
                    "one": {"baz": "baz"},
                },
            },
        ) == {
            "foo": {
                "one": "foofoo1",
                "two": "foo",
            },
            "bar": {
                "one": "bar",
                "bar": "bar",
                "deep": {
                    "one": "bar",
                },
            },
            "baz": {
                "one": {
                    "baz": "baz",
                },
            },
        }
