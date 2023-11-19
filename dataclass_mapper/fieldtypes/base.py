from typing import Any, List, Optional, Type
from abc import ABC, abstractmethod

class FieldType(ABC):
    all_field_types: List[Type["FieldType"]] = []

    def __init__(self, type_: Any, inner: Optional[List["FieldType"]] = None) -> None:
        self._type = type_
        self.inner = inner

    def __init_subclass__(cls: Type["FieldType"]) -> None:
        super().__init_subclass__()
        cls.all_field_types.append(cls)

    @staticmethod
    @abstractmethod
    def is_applicable(type_: Any) -> bool:
        pass

    @classmethod
    @abstractmethod
    def from_type(cls, type_: Any) -> "FieldType":
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    def __repr__(self) -> str:
        return f"{type(self).__name__}(type={self._type}, inner={repr(self.inner)})"

    def __eq__(self, other: "FieldType") -> bool:
        if type(self) is not type(other):
            return False
        return self.inner == other.inner


def compute_field_type(type_: Any) -> FieldType:
    for field_type in FieldType.all_field_types:
        if field_type.is_applicable(type_):
            return field_type.from_type(type_)

    raise NotImplementedError(f"Field type '{str(type_)}' is not supported.")
