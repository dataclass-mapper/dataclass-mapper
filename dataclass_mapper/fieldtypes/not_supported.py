from dataclasses import dataclass
from typing import Any

from dataclass_mapper.utils import get_class_name

from .base import FieldType


@dataclass
class NotSupportedFieldType(FieldType):
    type_: Any

    @staticmethod
    def is_applicable(type_: Any) -> bool:
        return False

    @classmethod
    def from_type(cls, type_: Any) -> "FieldType":
        return NotSupportedFieldType(type_=type_)

    def __str__(self) -> str:
        return get_class_name(self.type_)
