from enum import Enum
from typing import Any

from .implementations import class_meta_types
from .implementations.base import ClassMeta
from .namespace import Namespace


def get_class_meta(cls: Any, namespace: Namespace) -> ClassMeta:
    for class_meta_type in class_meta_types:
        if class_meta_type.applies(cls):
            return class_meta_type.from_clazz(cls, namespace=namespace)

    if issubclass(cls, Enum):
        raise ValueError("`mapper` does not support enum classes, use `enum_mapper` instead")
    raise NotImplementedError("only dataclasses and pydantic classes are supported")
