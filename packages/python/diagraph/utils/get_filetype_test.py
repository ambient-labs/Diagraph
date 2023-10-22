from pathlib import Path

import pytest

from .get_filetype import get_filetype


def describe_get_filetype():
    @pytest.mark.parametrize(
        ("filepath", "filetype", "expected"),
        [
            ("foo", None, "pickle"),
            ("foo.foo", None, "pickle"),
            ("foo.pkl", None, "pickle"),
            ("foo.json", None, "json"),
            ("foo.pkl", "foo", "pickle"),
            ("foo.json", "foo", "json"),
            ("foo.pkl", "pickle", "pickle"),
            ("foo.pkl", "json", "json"),
            ("foo.json", "pickle", "pickle"),
            ("foo.json", "json", "json"),
            (Path("foo.json"), None, "json"),
        ],
    )
    def test_it_returns_correct_filetype(filepath, filetype, expected):
        assert get_filetype(filepath, filetype) == expected
