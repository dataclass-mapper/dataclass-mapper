from dataclasses import MISSING, fields, is_dataclass, replace
from dataclasses import Field as DataclassField
from inspect import getsource
from typing import Any, Dict, cast, get_type_hints

from dataclass_mapper.fieldtypes.base import compute_field_type
from dataclass_mapper.namespace import Namespace

from .base import ClassMeta, DataclassType, FieldMeta
from .class_type import ClassType


class DataclassesFieldMeta(FieldMeta):
    @classmethod
    def from_dataclass(cls, field: DataclassField, real_type: Any) -> "DataclassesFieldMeta":
        has_default = field.default is not MISSING or field.default_factory is not MISSING
        field_meta = cls(
            attribute_name=field.name,
            type=compute_field_type(real_type),
            required=not has_default,
            initializer_param_name=field.name,
            init_with_ctor=True,
        )
        if not field.init:
            field_meta = replace(field_meta, required=False, init_with_ctor=False)
        return field_meta


class DataclassClassMeta(ClassMeta):
    _type = DataclassType.DATACLASSES

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
    def from_clazz(cls, clazz: Any, namespace: Namespace, type_: ClassType) -> "DataclassClassMeta":
        if not cls._has_autogenerated_init(clazz):
            raise NotImplementedError("only dataclasses with autogenerated __init__ are supported")
        return cls(name=cast(str, clazz.__name__), fields=cls._fields(clazz, namespace), clazz=clazz)

    @staticmethod
    def _has_autogenerated_init(clazz: Any) -> bool:
        if not clazz.__dataclass_params__.init:
            return False
        try:
            getsource(clazz.__init__)
            return False
        except OSError:
            return True
