from typing import Any, get_args, get_origin

from .base import FieldType
from .compute import compute_field_type


class DictFieldType(FieldType):
    def __init__(self, key_type: FieldType, value_type: FieldType):
        self.key_type = key_type
        self.value_type = value_type

    @staticmethod
    def is_applicable(type_: Any) -> bool:
        return get_origin(type_) is dict

    @classmethod
    def from_type(cls, type_: Any) -> FieldType:
        key_type, value_type = [compute_field_type(t) for t in get_args(type_)]
        return cls(key_type, value_type)

    def __str__(self) -> str:
        return f"Dict[{self.key_type}, {self.value_type}]"

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return False
        assert isinstance(other, DictFieldType)
        return self.key_type == other.key_type and self.value_type == other.value_type
