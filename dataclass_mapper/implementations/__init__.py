from typing import List, Type

from .base import ClassMeta, DataclassType, FieldMeta
from .dataclasses import DataclassClassMeta
from .pydantic_v1 import PydanticV1ClassMeta

class_meta_types: List[Type[ClassMeta]] = [DataclassClassMeta, PydanticV1ClassMeta]

__all__ = ["FieldMeta", "ClassMeta", "DataclassType", "class_meta_types"]
