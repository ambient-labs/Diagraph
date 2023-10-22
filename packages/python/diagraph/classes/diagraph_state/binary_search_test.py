import pytest

from .binary_search import (
    binary_search,
)


def describe_binary_search():
    def test_it_returns_none_for_empty_array():
        assert binary_search([], 0, 0, 1) is None

    @pytest.mark.parametrize(
        ("key", "value"),
        [
            (10, 0),
            (11, 1),
            (12, 2),
        ],
    )
    def test_it_returns_index_for_match(key, value):
        arr = [10, 11, 12]
        assert binary_search(arr, key) == value

    @pytest.mark.parametrize(
        ("key", "value"),
        [
            (10.1, 0),
            (11.1, 1),
            (12.1, 2),
        ],
    )
    def test_it_returns_index_for_match_with_floats(key, value):
        arr = [10.1, 11.1, 12.1]
        assert binary_search(arr, key) == value

    @pytest.mark.parametrize(
        ("key", "value"),
        [
            (11, 0),
            (13, 1),
            (15, 2),
            (25, 2),
        ],
    )
    def test_it_returns_closest_index_for_match(key, value):
        arr = [10, 12, 14]
        assert binary_search(arr, key) == value

    @pytest.mark.parametrize(
        ("key", "value"),
        [
            (9, -1),
            (1, -1),
            (0, -1),
            (-1, -1),
        ],
    )
    def test_it_returns_none_for_earlier_values(key, value):
        arr = [10, 12, 14]
        assert binary_search(arr, key) is None
