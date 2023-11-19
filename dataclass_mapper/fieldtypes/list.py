from typing import Any
from .base import FieldType, compute_field_type
from typing import get_args, get_origin, Any


class ListFieldType(FieldType):
    @staticmethod
    def is_applicable(type_: Any) -> bool:
        return get_origin(type_) is list

    @classmethod
    def from_type(cls, type_: Any) -> FieldType:
        inner = [compute_field_type(get_args(type_)[0])]
        return cls(type_=type_, inner=inner)

    def __str__(self) -> str:
        assert self.inner, "a list type cannot be empty"
        return f"List[{str(self.inner[0])}]"
