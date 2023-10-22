import pytest

from .diagraph_state_record import (
    DiagraphStateRecord,
    DiagraphStateValue,
    DiagraphStateValueEmpty,
)


def describe_diagraph_state_value_empty():
    def test_it_returns_true_if_instance():
        assert 1 != DiagraphStateValueEmpty()
        assert DiagraphStateValueEmpty() == DiagraphStateValueEmpty()


def describe_diagraph_state_record_test():
    def test_it_returns_empty_for_a_record_without_keys():
        record = DiagraphStateRecord()
        assert record[1] == DiagraphStateValueEmpty()

    def test_it_returns_record_for_matching_key():
        record = DiagraphStateRecord()
        record[1] = "foo"
        value = record[1]
        assert isinstance(value, DiagraphStateValue)
        assert value.value == "foo"

    def test_it_returns_none_for_matching_key():
        record = DiagraphStateRecord()
        record[1] = None
        value = record[1]
        assert isinstance(value, DiagraphStateValue)
        assert value.value is None

    def test_it_returns_empty_for_matching_key():
        record = DiagraphStateRecord()
        record[1] = DiagraphStateValueEmpty()
        assert record[1] == DiagraphStateValueEmpty()

    def test_it_does_not_append_matching_keys():
        record = DiagraphStateRecord()
        record[1] = DiagraphStateValueEmpty()
        record[1] = "foo"
        record[1] = "bar"
        value = record[1]
        assert isinstance(value, DiagraphStateValue)
        assert value.value == "bar"

    @pytest.mark.parametrize(
        ("key", "expectation"),
        [(0, "foo"), (1, "bar"), (2, "baz")],
    )
    def test_it_returns_record_for_matching_key_for_multiple_keys(key, expectation):
        record = DiagraphStateRecord()
        record[0] = "foo"
        record[1] = "bar"
        record[2] = "baz"
        value = record[key]
        assert isinstance(value, DiagraphStateValue)
        assert value.value == expectation

    @pytest.mark.parametrize(
        ("key", "expectation"),
        [
            (1, "foo"),
            (3, "bar"),
            (5, "baz"),
        ],
    )
    def test_it_returns_closest_earliest_record(key, expectation):
        record = DiagraphStateRecord()
        record[0] = "foo"
        record[2] = "bar"
        record[4] = "baz"
        value = record[key]
        assert isinstance(value, DiagraphStateValue)
        assert value.value == expectation

    @pytest.mark.parametrize(
        ("key", "expectation"),
        [
            (1, "foo"),
            (2, "foo"),
            (3, "foo"),
            (4, "foo"),
            (5, "bar"),
            (6, "bar"),
            (7, "bar"),
            (8, "bar"),
            (9, "bar"),
            (10, "baz"),
            (11, "baz"),
            (12, "baz"),
        ],
    )
    def test_it_returns_closest_earliest_record_for_wider_records(key, expectation):
        record = DiagraphStateRecord()
        record[1] = "foo"
        record[5] = "bar"
        record[10] = "baz"
        value = record[key]
        assert isinstance(value, DiagraphStateValue)
        assert value.value == expectation

    @pytest.mark.parametrize(
        ("key"),
        [(-2), (-1), (0), (1)],
    )
    def test_it_returns_empty_for_a_key_prior_to_any_record(
        key,
    ):
        record = DiagraphStateRecord()
        record[2] = "bar"
        assert record[key] == DiagraphStateValueEmpty()
