from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Optional
from uuid import uuid4

import dataclass_mapper.code_generator as cg
from dataclass_mapper.fieldtypes import FieldType
from dataclass_mapper.namespace import Namespace


class DataclassType(Enum):
    DATACLASSES = auto()
    PYDANTIC = auto()
    SQLAlchemy = auto()


@dataclass
class FieldMeta:
    """Dataclass containing meta information about fields in dataclasses or pydantic classes.
    Information like the name and type of the field, and if it is required to set it.

    The type will contain the exact type of the field.
    However for optional fields, the Optional quantifier is removed, and `allow_none` is set accordingly.
    - int           => type = int, allow_none = False
    - Optional[int] => type = int, allow_none = True
    """

    name: str
    type: FieldType
    # allow_none: bool
    required: bool
    alias: Optional[str] = None

    # @property
    # def disallow_none(self) -> bool:
    #     return not self.allow_none

    def __repr__(self) -> str:
        return f"'{self.name}' of type '{self.type}'"


class ClassMeta(ABC):
    _type: DataclassType

    def __init__(self, name: str, fields: Dict[str, FieldMeta], clazz: Any, alias_name: Optional[str] = None) -> None:
        self.name = name
        self.fields = fields
        self.alias_name = alias_name or f"_{uuid4().hex}"
        self.clazz = clazz

    def return_statement(self) -> cg.Return:
        """The code for creating the object and returning it"""
        return cg.Return(f"{self.alias_name}(**d)")

    @abstractmethod
    def get_assignment_name(self, field: FieldMeta) -> str:
        """Returns the name for the variable that should be used for an assignment"""

    @staticmethod
    @abstractmethod
    def applies(clz: Any) -> bool:
        """Determines if the current implementation can supports the provided class"""

    @classmethod
    @abstractmethod
    def from_clazz(cls, clazz: Any, namespace: Namespace) -> "ClassMeta":
        """Parse the given class"""

    @classmethod
    def post_process(
        cls, code: cg.Statement, source_cls: Any, target_field: FieldMeta, source_field: FieldMeta
    ) -> cg.Statement:
        """Modifies the generated code for one field mapping if needed"""
        return code
