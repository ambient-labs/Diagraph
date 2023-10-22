from collections.abc import Callable
from time import time

from .diagraph_state_record import (
    DiagraphStateRecord,
    DiagraphStateValue,
)
from .types import StateKey, StateValue

TupleWithTimestamp = tuple[StateKey, float]


class DiagraphState:
    __internal_state__: dict[StateKey, DiagraphStateRecord]
    timestamps: list[float]

    def __init__(self) -> None:
        self.__internal_state__ = {}
        self.timestamps = [time()]

    def __setitem__(self, key: StateKey, value: StateValue) -> None:
        record = self.__internal_state__.get(key)
        if record is None:
            record = DiagraphStateRecord()
            self.__internal_state__[key] = record
        record[self.current_timestamp] = value

    def __get_key_and_timestamp__(
        self,
        key: StateKey | TupleWithTimestamp,
    ) -> TupleWithTimestamp:
        if isinstance(key[0], str):
            return key, self.current_timestamp
        key, timestamp = key
        return key, timestamp

    def __getitem__(self, key: StateKey | TupleWithTimestamp) -> StateValue:
        key, timestamp = self.__get_key_and_timestamp__(key)
        # validate_key(key[0])
        record = self.__internal_state__.get(key, None)
        if record is None:
            state = {key: str(val) for key, val in self.__internal_state__.items()}
            raise Exception(f"No record for {get_key(key)}, {state}")
        value = record[timestamp]
        if isinstance(value, DiagraphStateValue):
            return value.value
        raise Exception(f"Value for {get_key(key)} is explicitly unset")

    def add_timestamp(self) -> float:
        current_time = time()
        self.timestamps.append(current_time)
        return current_time

    @property
    def current_timestamp(self):
        return self.timestamps[-1]


def get_key(key: StateKey):
    return ".".join([get_name(f) for f in reversed(list(key))])


def get_name(f: str | Callable) -> str:
    if isinstance(f, str):
        return f
    return f.__name__


# def validate_key(key: str):
#     if key not in ['prompt', 'result', 'error']:
#         raise Exception(f'Invalid key: {key}')
