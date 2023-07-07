from dataclasses import MISSING, fields, is_dataclass
from dataclasses import Field as DataclassField
from typing import Any, Dict, cast, get_args, get_type_hints

from dataclass_mapper.namespace import Namespace
from dataclass_mapper.utils import is_optional

from .base import ClassMeta, DataclassType, FieldMeta


class DataclassesFieldMeta(FieldMeta):
    @classmethod
    def from_dataclass(cls, field: DataclassField, real_type: Any) -> "DataclassesFieldMeta":
        has_default = field.default is not MISSING or field.default_factory is not MISSING
        if is_optional(real_type):
            real_types = [t for t in get_args(real_type) if t is not type(None)]
            assert len(real_types) == 1
            return cls(
                name=field.name,
                type=real_types[0],
                allow_none=True,
                required=not has_default,
            )
        else:
            return cls(
                name=field.name,
                type=real_type,
                allow_none=False,
                required=not has_default,
            )


class DataclassClassMeta(ClassMeta):
    _type = DataclassType.DATACLASSES

    def get_assignment_name(self, field: FieldMeta) -> str:
        return field.name

    @staticmethod
    def _fields(clazz: Any, namespace: Namespace) -> Dict[str, FieldMeta]:
        real_types = get_type_hints(clazz, globalns=namespace.globals, localns=namespace.locals)
        return {
            field.name: DataclassesFieldMeta.from_dataclass(field, real_type=real_types[field.name])
            for field in fields(clazz)
        }

    @staticmethod
    def applies(clz: Any) -> bool:
        return cast(bool, is_dataclass(clz))

    @classmethod
    def from_clazz(cls, clazz: Any, namespace: Namespace) -> "DataclassClassMeta":
        return cls(name=cast(str, clazz.__name__), fields=cls._fields(clazz, namespace))
