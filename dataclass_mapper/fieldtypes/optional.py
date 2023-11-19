from typing import Any

from dataclass_mapper.utils import is_optional, remove_NoneType

from .base import FieldType, compute_field_type
from .union import UnionFieldType


class OptionalFieldType(FieldType):
    @staticmethod
    def is_applicable(type_: Any) -> bool:
        return is_optional(type_)

    @classmethod
    def from_type(cls, type_: Any) -> FieldType:
        inner = [compute_field_type(remove_NoneType(type_))]
        return cls(type_=type_, inner=inner)

    def __str__(self) -> str:
        assert self.inner, "a optional type cannot be empty"

        # Nicer Output for Union[int, str, None], which would be OptionalFieldType[UnionFieldType[...]]
        if isinstance(self.inner[0], UnionFieldType):
            assert self.inner[0].inner, "a union type cannot be empty"
            ts = ", ".join(str(t) for t in self.inner[0].inner)
            return f"Union[{ts}, None]"
        else:
            return f"Optional[{str(self.inner[0])}]"
