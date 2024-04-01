from typing import Any

import dataclass_mapper.code_generator as cg
from dataclass_mapper.fieldtypes import compute_field_type
from dataclass_mapper.namespace import Namespace

from .base import ClassMeta, DataclassType, FieldMeta
from .class_type import ClassType


class SimpleType(ClassMeta):
    """A simple type, e.g. just a string. To allow mappings of the form `SomeDataclass -> str`."""

    _type = DataclassType.SIMPLETYPE

    def constructor_call(self) -> cg.Expression:
        """The code for creating the object"""
        return cg.NONE

    @staticmethod
    def applies(clz: Any) -> bool:
        """Determines if the current implementation can supports the provided class"""
        return True

    @classmethod
    def from_clazz(cls, clazz: Any, namespace: Namespace, type_: ClassType) -> "ClassMeta":
        """Parse the given class"""
        return cls(
            name="simple",
            fields={
                "": FieldMeta(
                    attribute_name="",
                    type=compute_field_type(clazz),
                    required=True,
                    initializer_param_name="",
                    init_with_ctor=False,
                )
            },
            clazz=clazz,
        )
