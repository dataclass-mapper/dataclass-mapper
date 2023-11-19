from typing import Any
from .base import FieldType, compute_field_type
from typing import get_args, get_origin, Any
from .utils import is_union_type, is_optional


class UnionFieldType(FieldType):
    @staticmethod
    def is_applicable(type_: Any) -> bool:
        return is_union_type(type_) and not is_optional(type_)

    @classmethod
    def from_type(cls, type_: Any) -> FieldType:
        inner = [compute_field_type(t) for t in get_args(type_)]
        return cls(type_=type_, inner=inner)

    def __str__(self) -> str:
        assert self.inner, "a union cannot be empty"
        ts = ", ".join(str(t) for t in self.inner)
        return f"Union[{ts}]"
