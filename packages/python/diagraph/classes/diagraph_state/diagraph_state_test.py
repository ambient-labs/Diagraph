import pytest

from .diagraph_state import DiagraphState
from .diagraph_state_record import DiagraphStateValueEmpty


def describe_diagraph_state():
    def test_it_sets_values():
        state = DiagraphState()
        state[
            tuple(
                "foo",
            )
        ] = "foo"
        state[
            tuple(
                "bar",
            )
        ] = "bar"
        assert state[tuple("foo")] == "foo"
        assert state[tuple("bar")] == "bar"

    def test_it_sets_none_values():
        state = DiagraphState()
        state[
            tuple(
                "foo",
            )
        ] = None
        assert state[tuple("foo")] is None

    def test_it_raises_for_no_value():
        state = DiagraphState()
        with pytest.raises(Exception, match="No record"):
            state[
                tuple(
                    "foo",
                )
            ]

    def test_it_raises_for_empty_value():
        state = DiagraphState()
        state[
            tuple(
                "foo",
            )
        ] = DiagraphStateValueEmpty()
        with pytest.raises(Exception, match="unset"):
            state[
                tuple(
                    "foo",
                )
            ]

    def test_it_returns_current_timestamp_value():
        state = DiagraphState()
        state[
            tuple(
                "foo",
            )
        ] = "foo"
        state.add_timestamp()
        state[
            tuple(
                "foo",
            )
        ] = "bar"

        assert state[tuple("foo")] == "bar"

    def test_it_returns_previous_timestamp_value():
        state = DiagraphState()
        state[
            tuple(
                "foo",
            )
        ] = "foo"
        state.add_timestamp()
        state[
            tuple(
                "foo",
            )
        ] = "bar"
        state.add_timestamp()
        state[
            tuple(
                "baz",
            )
        ] = "baz"

        assert state[tuple("foo")] == "bar"

    def test_it_returns_value_for_specific_timestamp():
        state = DiagraphState()
        current_time = state.current_timestamp
        state[
            tuple(
                "foo",
            )
        ] = "foo"
        state.add_timestamp()
        state[
            tuple(
                "foo",
            )
        ] = "bar"

        assert state[tuple("foo"), state.current_timestamp] == "bar"
        assert state[tuple("foo"), current_time] == "foo"

    @pytest.mark.parametrize(
        ("index", "expectation"),
        [
            (0, "foo"),
            (1, "foo"),
            (2, "bar"),
            (3, "bar"),
            (4, "bar"),
        ],
    )
    def test_it_returns_previous_value_for_specific_timestamp(index, expectation):
        state = DiagraphState()
        state[
            tuple(
                "foo",
            )
        ] = "foo"
        timestamps: list[float] = [state.current_timestamp]
        timestamps.extend([state.add_timestamp(), state.add_timestamp()])
        state[
            tuple(
                "foo",
            )
        ] = "bar"
        timestamps.extend([state.add_timestamp(), state.add_timestamp()])

        assert state[tuple("foo"), timestamps[index]] == expectation
