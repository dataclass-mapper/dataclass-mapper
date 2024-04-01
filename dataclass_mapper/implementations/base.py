from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Optional
from uuid import uuid4

import dataclass_mapper.code_generator as cg
from dataclass_mapper.fieldtypes import FieldType
from dataclass_mapper.namespace import Namespace

from .class_type import ClassType


class DataclassType(Enum):
    DATACLASSES = auto()
    PYDANTIC = auto()
    SQLALCHEMY = auto()
    SIMPLETYPE = auto()


@dataclass(frozen=True)
class FieldMeta:
    """Dataclass containing meta information about fields in dataclasses or pydantic classes.
    Information like the name and type of the field, and if it is required to set it.
    """

    # The name to access this field, via obj.{attribute_name}
    attribute_name: str
    type: FieldType
    required: bool
    # The name that's used in the initializer method, via Target({initializer_param_name}=...)
    # Typically that's the same as the attribute name, however in certain cases (alias in Pydantic) it may differ.
    initializer_param_name: str
    init_with_ctor: bool

    def __repr__(self) -> str:
        return f"'{self.attribute_name}' of type '{self.type}'"


class ClassMeta(ABC):
    _type: DataclassType

    def __init__(
        self, name: str, fields: Dict[str, FieldMeta], clazz: Any, internal_name: Optional[str] = None
    ) -> None:
        self.name = name
        self.fields = fields
        # For the code generation it's better to have a unique name.
        # E.g. to avoid cases where two classes are named the same and it might create the wrong one
        self.internal_name = internal_name or f"_{uuid4().hex}"
        self.clazz = clazz

    def constructor_call(self) -> cg.Expression:
        """The code for creating the object"""
        return cg.FunctionCall(cg.Variable(self.internal_name), args=[], keywords=[cg.Keyword(cg.Variable("d"))])

    @staticmethod
    @abstractmethod
    def applies(clz: Any) -> bool:
        """Determines if the current implementation can supports the provided class"""

    @classmethod
    @abstractmethod
    def from_clazz(cls, clazz: Any, namespace: Namespace, type_: ClassType) -> "ClassMeta":
        """Parse the given class"""

    @classmethod
    def skip_condition(cls, target_field: FieldMeta, source_field: FieldMeta) -> Optional[cg.Expression]:
        return None
