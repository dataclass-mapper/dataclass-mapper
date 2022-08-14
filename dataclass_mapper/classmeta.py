from dataclasses import dataclass, field, is_dataclass
from enum import Enum, auto
from typing import Any
from uuid import uuid4


class DataclassType(Enum):
    DATACLASSES = auto()
    PYDANTIC = auto()


@dataclass
class ClassMeta:
    name: str
    _type: DataclassType
    alias_name: str = field(default_factory=lambda: f"_{uuid4().hex}")

    @classmethod
    def from_class(cls, clazz: Any):
        return cls(
            name=clazz.__name__,
            _type=get_dataclass_type(clazz),
        )


def get_dataclass_type(cls: Any) -> DataclassType:
    if is_dataclass(cls):
        return DataclassType.DATACLASSES
    try:
        pydantic = __import__("pydantic")
        if issubclass(cls, pydantic.BaseModel):
            return DataclassType.PYDANTIC
    except ImportError:
        pass
    raise NotImplementedError("only dataclasses and pydantic classes are supported")
