from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Optional, cast
from uuid import uuid4


class DataclassType(Enum):
    DATACLASSES = auto()
    PYDANTIC = auto()


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
    type: Any
    allow_none: bool
    required: bool
    alias: Optional[str] = None

    @property
    def disallow_none(self) -> bool:
        return not self.allow_none

    @property
    def type_string(self) -> str:
        try:
            type_name = cast(str, self.type.__name__)
        except Exception:
            type_name = str(self.type)
        if self.allow_none:
            type_name = f"Optional[{type_name}]"
        return type_name

    def __repr__(self) -> str:
        return f"'{self.name}' of type '{self.type_string}'"


class ClassMeta(ABC):
    _type: DataclassType

    def __init__(self, name: str, fields: Dict[str, FieldMeta], alias_name: Optional[str] = None) -> None:
        self.name = name
        self.fields = fields
        self.alias_name = alias_name or f"_{uuid4().hex}"

    @abstractmethod
    def return_statement(self) -> str:
        ...

    @abstractmethod
    def get_assignment_name(self, field: FieldMeta) -> str:
        """Returns the name for the variable that should be used for an assignment"""
