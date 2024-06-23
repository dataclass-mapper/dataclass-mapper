from typing import Any

from dataclass_mapper.fieldtypes.utils import remove_NoneType
from dataclass_mapper.utils import is_optional

from .base import FieldType
from .compute import compute_field_type
from .union import UnionFieldType


class OptionalFieldType(FieldType):
    def __init__(self, inner_type: FieldType):
        self.inner_type = inner_type

    @staticmethod
    def is_applicable(type_: Any) -> bool:
        return is_optional(type_)

    @classmethod
    def from_type(cls, type_: Any) -> FieldType:
        inner = compute_field_type(remove_NoneType(type_))
        return cls(inner)

    def __str__(self) -> str:
        # Nicer Output for Union[int, str, None], which would be OptionalFieldType[UnionFieldType[...]]
        if isinstance(self.inner_type, UnionFieldType):
            ts = ", ".join(str(t) for t in self.inner_type.inner_types)
            return f"Union[{ts}, None]"
        else:
            return f"Optional[{self.inner_type}]"

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return False
        assert isinstance(other, OptionalFieldType)
        return self.inner_type == other.inner_type
