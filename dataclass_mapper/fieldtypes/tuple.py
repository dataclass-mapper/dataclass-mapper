from typing import Any, List, get_args, get_origin

from .base import FieldType
from .compute import compute_field_type


class TupleFieldType(FieldType):
    def __init__(self, value_types: List[FieldType]):
        self.value_types = value_types

    @staticmethod
    def is_applicable(type_: Any) -> bool:
        return get_origin(type_) is tuple

    @classmethod
    def from_type(cls, type_: Any) -> FieldType:
        value_types = [compute_field_type(element_type) for element_type in get_args(type_)]
        return cls(value_types)

    def __str__(self) -> str:
        elements = ", ".join(str(element_type) for element_type in self.value_types)
        return f"Tuple[{elements}]"

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return False
        assert isinstance(other, TupleFieldType)
        return self.value_types == other.value_types
