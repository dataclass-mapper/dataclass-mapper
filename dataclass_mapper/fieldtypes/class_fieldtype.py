from sqlalchemy.dialects.postgresql import Any
from .base import FieldType
from typing import cast, get_origin, Any


class ClassFieldType(FieldType):
    @staticmethod
    def is_applicable(type_: Any) -> bool:
        return get_origin(type_) is None

    @classmethod
    def from_type(cls, type_: Any) -> "FieldType":
        return cls(type_)

    def __str__(self) -> str:
        try:
            return cast(str, self._type.__name__)
        except Exception:
            return str(self._type)

    def __eq__(self, other: "FieldType") -> bool:
        if type(self) is not type(other):
            return False
        return self._type == other._type
