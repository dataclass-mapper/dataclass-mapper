from dataclasses import is_dataclass
from enum import Enum
from typing import Any

from .implementations.base import ClassMeta
from .implementations.dataclasses import DataclassClassMeta
from .implementations.pydantic_v1 import PydanticV1ClassMeta
from .namespace import Namespace


def get_class_meta(cls: Any, namespace: Namespace) -> ClassMeta:
    if is_dataclass(cls):
        return DataclassClassMeta.from_clazz(cls, namespace=namespace)
    try:
        pydantic = __import__("pydantic")
        if issubclass(cls, pydantic.BaseModel):
            return PydanticV1ClassMeta.from_clazz(cls, namespace=namespace)
    except ImportError:
        pass

    if issubclass(cls, Enum):
        raise ValueError("`mapper` does not support enum classes, use `enum_mapper` instead")
    raise NotImplementedError("only dataclasses and pydantic classes are supported")
