from typing import Any

from .base import FieldType


class AnyFieldType(FieldType):
    @staticmethod
    def is_applicable(type_: Any) -> bool:
        return type_ is Any

    @classmethod
    def from_type(cls, type_: Any) -> FieldType:
        return cls()

    def __str__(self) -> str:
        return "Any"

    def __eq__(self, other: object) -> bool:
        return type(self) is type(other)
