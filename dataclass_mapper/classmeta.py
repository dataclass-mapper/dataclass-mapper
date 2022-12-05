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
    has_validators: bool
    alias_name: str = field(default_factory=lambda: f"_{uuid4().hex}")

    @classmethod
    def from_class(cls, clazz: Any):
        _type = get_dataclass_type(clazz)

        return cls(
            name=clazz.__name__,
            _type=_type,
            has_validators=has_validators(clazz, _type)
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


def has_validators(cls: Any, _type: DataclassType) -> bool:
    if _type == DataclassType.DATACLASSES:
        return False
    elif _type == DataclassType.PYDANTIC:
        return bool(cls.__validators__) or bool(cls.__pre_root_validators__) or bool(cls.__post_root_validators__)
    raise NotImplementedError("only dataclasses and pydantic classes are supported")
