# If no timestamp exists, return an empty
# Else, return the matching timestamp if one exists
# Else, return the closest previous timestamp, if one exists
from ..ordered_set import OrderedSet
from .binary_search import binary_search
from .types import StateValue


class DiagraphStateValue:
    value: StateValue

    def __init__(self, value: StateValue):
        self.value = value

    def __str__(self) -> str:
        return f"{self.value}"


class DiagraphStateValueEmpty:
    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __str__(self) -> str:
        return "novalue"


RecordValue = DiagraphStateValue | DiagraphStateValueEmpty


class DiagraphStateRecord:
    values: dict[float, RecordValue]
    keys: OrderedSet[float]

    def __init__(self):
        self.values = {}
        self.keys = OrderedSet()

    def __setitem__(self, key: float, value: StateValue) -> None:
        self.keys.add(key)
        if value == DiagraphStateValueEmpty():
            self.values[key] = value
        else:
            self.values[key] = DiagraphStateValue(value)

    def __getitem__(self, key: float) -> RecordValue:
        closest_key_idx = binary_search(list(self.keys), key)
        if closest_key_idx is None:
            return DiagraphStateValueEmpty()
        closest_key = self.keys[closest_key_idx]
        return self.values.get(closest_key, DiagraphStateValueEmpty())

    def __str__(self) -> str:
        values = {key: str(val) for key, val in self.values.items()}
        return f"DiagraphStateRecord<{values}>"
