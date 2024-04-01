from enum import Enum
from typing import Any

from dataclass_mapper.implementations.simple_type import SimpleType

from .implementations import class_meta_types
from .implementations.base import ClassMeta
from .implementations.class_type import ClassType
from .namespace import Namespace


def get_class_meta(cls: Any, namespace: Namespace, type_: ClassType = ClassType.TARGET) -> ClassMeta:
    for class_meta_type in class_meta_types:
        if class_meta_type.applies(cls):
            return class_meta_type.from_clazz(cls, namespace=namespace, type_=type_)

    if issubclass(cls, Enum):
        raise ValueError("`mapper` does not support enum classes, use `enum_mapper` instead")
    raise NotImplementedError("only dataclasses, pydantic and sqlalchemy classes are supported")


def is_dataclass_supported(cls: Any) -> bool:
    return any(class_meta_type.applies(cls) for class_meta_type in class_meta_types if class_meta_type != SimpleType)
