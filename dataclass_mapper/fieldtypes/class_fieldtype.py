from typing import Any, cast, get_origin

from .base import FieldType


class ClassFieldType(FieldType):
    def __init__(self, cls_type: Any):
        self.cls_type = cls_type

    @staticmethod
    def is_applicable(type_: Any) -> bool:
        return get_origin(type_) is None and type_ is not Any

    @classmethod
    def from_type(cls, type_: Any) -> "FieldType":
        return cls(type_)

    def __str__(self) -> str:
        try:
            return cast(str, self.cls_type.__name__)
        except Exception:
            return str(self.cls_type)

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return False
        assert isinstance(other, ClassFieldType)
        return cast(bool, self.cls_type == other.cls_type)
