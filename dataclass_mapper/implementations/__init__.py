from typing import List, Type

from .base import ClassMeta, DataclassType, FieldMeta
from .dataclasses import DataclassClassMeta
from .pydantic_v1 import PydanticV1ClassMeta
from .pydantic_v2 import PydanticV2ClassMeta
from .simple_type import SimpleType
from .sqlalchemy import SQLAlchemyClassMeta

class_meta_types: List[Type[ClassMeta]] = [
    PydanticV1ClassMeta,
    PydanticV2ClassMeta,
    SQLAlchemyClassMeta,
    # SQLAlchemy has a dataclass mode (MappedAsDataclass), those would wrongly detected by the DataclassClassMeta.
    # So we need to run the SQLAlchemyClassMeta detection ahead of the SQLAlchemyClassMeta.
    DataclassClassMeta,
    SimpleType,
]

__all__ = ["FieldMeta", "ClassMeta", "DataclassType", "class_meta_types"]
