from abc import ABC, abstractmethod
from dataclasses import fields, is_dataclass
from enum import Enum, auto
from typing import Any, Dict, Optional, cast, get_type_hints
from uuid import uuid4

from .fieldmeta import FieldMeta
from .namespace import Namespace


class DataclassType(Enum):
    DATACLASSES = auto()
    PYDANTIC = auto()


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


class DataclassClassMeta(ClassMeta):
    _type = DataclassType.DATACLASSES

    def return_statement(self) -> str:
        return f"{self.alias_name}(**d)"

    def get_assignment_name(self, field: FieldMeta) -> str:
        return field.name

    @staticmethod
    def _fields(clazz: Any, namespace: Namespace) -> Dict[str, FieldMeta]:
        real_types = get_type_hints(clazz, globalns=namespace.globals, localns=namespace.locals)
        return {
            field.name: FieldMeta.from_dataclass(field, real_type=real_types[field.name]) for field in fields(clazz)
        }

    @classmethod
    def from_clazz(cls, clazz: Any, namespace: Namespace) -> "DataclassClassMeta":
        return cls(name=cast(str, clazz.__name__), fields=cls._fields(clazz, namespace))


class PydanticClassMeta(ClassMeta):
    _type = DataclassType.PYDANTIC

    def __init__(
        self,
        name: str,
        fields: Dict[str, FieldMeta],
        use_construct: bool,
        allow_population_by_field_name: bool = False,
        alias_name: Optional[str] = None,
    ) -> None:
        super().__init__(name=name, fields=fields, alias_name=alias_name)
        self.use_construct = use_construct
        self.allow_population_by_field_name = allow_population_by_field_name

    @staticmethod
    def has_validators(clazz: Any) -> bool:
        return bool(clazz.__validators__) or bool(clazz.__pre_root_validators__) or bool(clazz.__post_root_validators__)

    def return_statement(self) -> str:
        if self.use_construct:
            return f"{self.alias_name}.construct(**d)"
        else:
            return f"{self.alias_name}(**d)"

    def get_assignment_name(self, field: FieldMeta) -> str:
        if self.use_construct or self.allow_population_by_field_name:
            return field.name
        else:
            return field.alias or field.name

    @staticmethod
    def _fields(clazz: Any, namespace: Namespace) -> Dict[str, FieldMeta]:
        clazz.update_forward_refs(**namespace.locals)
        return {field.name: FieldMeta.from_pydantic(field) for field in clazz.__fields__.values()}

    @classmethod
    def from_clazz(cls, clazz: Any, namespace: Namespace) -> "PydanticClassMeta":
        return cls(
            name=cast(str, clazz.__name__),
            fields=cls._fields(clazz, namespace=namespace),
            use_construct=not cls.has_validators(clazz),
            allow_population_by_field_name=getattr(clazz.Config, "allow_population_by_field_name", False),
        )


def get_class_meta(cls: Any, namespace: Namespace) -> ClassMeta:
    if is_dataclass(cls):
        return DataclassClassMeta.from_clazz(cls, namespace=namespace)
    try:
        pydantic = __import__("pydantic")
        if issubclass(cls, pydantic.BaseModel):
            return PydanticClassMeta.from_clazz(cls, namespace=namespace)
    except ImportError:
        pass

    if issubclass(cls, Enum):
        raise ValueError("`mapper` does not support enum classes, use `enum_mapper` instead")
    raise NotImplementedError("only dataclasses and pydantic classes are supported")
