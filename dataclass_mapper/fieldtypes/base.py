from abc import ABC, abstractmethod
from typing import Any, ClassVar, List, Type


class FieldType(ABC):
    all_field_types: ClassVar[List[Type["FieldType"]]] = []

    def __init_subclass__(cls: Type["FieldType"]) -> None:
        super().__init_subclass__()
        cls.all_field_types.append(cls)

    @staticmethod
    @abstractmethod
    def is_applicable(type_: Any) -> bool:
        """Can the source type be converted to the target type"""

    @classmethod
    @abstractmethod
    def from_type(cls, type_: Any) -> "FieldType":
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass
