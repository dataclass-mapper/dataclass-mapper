from typing import Any, List, get_args

from .base import FieldType
from .compute import compute_field_type
from .utils import is_optional, is_union_type


class UnionFieldType(FieldType):
    def __init__(self, inner_types: List[FieldType]):
        self.inner_types = inner_types

    @staticmethod
    def is_applicable(type_: Any) -> bool:
        return is_union_type(type_) and not is_optional(type_)

    @classmethod
    def from_type(cls, type_: Any) -> FieldType:
        inner = [compute_field_type(t) for t in get_args(type_)]
        return cls(inner)

    def __str__(self) -> str:
        ts = ", ".join(str(t) for t in self.inner_types)
        return f"Union[{ts}]"

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return False
        assert isinstance(other, UnionFieldType)
        return self.inner_types == other.inner_types
