from typing import Any, get_args, get_origin

from .base import FieldType
from .compute import compute_field_type


class ListFieldType(FieldType):
    def __init__(self, value_type: FieldType):
        self.value_type = value_type

    @staticmethod
    def is_applicable(type_: Any) -> bool:
        return get_origin(type_) is list

    @classmethod
    def from_type(cls, type_: Any) -> FieldType:
        value_type = compute_field_type(get_args(type_)[0])
        return cls(value_type)

    def __str__(self) -> str:
        return f"List[{self.value_type}]"

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return False
        assert isinstance(other, ListFieldType)
        return self.value_type == other.value_type
