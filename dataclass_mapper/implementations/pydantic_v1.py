from typing import Any, Dict, Optional, Tuple, cast

import dataclass_mapper.code_generator as cg
from dataclass_mapper.fieldtypes import OptionalFieldType, compute_field_type
from dataclass_mapper.namespace import Namespace

from .base import ClassMeta, DataclassType, FieldMeta
from .class_type import ClassType
from .utils import parse_version


def pydantic_version() -> Tuple[int, int, int]:
    try:
        pydantic = __import__("pydantic")
        return parse_version(cast(str, pydantic.__version__))
    except ModuleNotFoundError:
        return (0, 0, 0)


class PydanticV1FieldMeta(FieldMeta):
    @classmethod
    def from_pydantic(cls, field: Any, use_alias_in_initializer: bool) -> "PydanticV1FieldMeta":
        type_ = field.outer_type_
        if field.allow_none:
            type_ = Optional[type_]

        initializer_param_name = field.name
        if use_alias_in_initializer:
            initializer_param_name = field.alias or field.name

        return cls(
            attribute_name=field.name,
            type=compute_field_type(type_),
            required=field.required,
            initializer_param_name=initializer_param_name,
            init_with_ctor=True,
        )


class PydanticV1ClassMeta(ClassMeta):
    _type = DataclassType.PYDANTIC

    def __init__(
        self,
        name: str,
        fields: Dict[str, FieldMeta],
        clazz: Any,
        use_construct: bool,
        internal_name: Optional[str] = None,
    ) -> None:
        super().__init__(name=name, fields=fields, internal_name=internal_name, clazz=clazz)
        self.use_construct = use_construct

    @staticmethod
    def has_validators(clazz: Any) -> bool:
        return bool(clazz.__validators__) or bool(clazz.__pre_root_validators__) or bool(clazz.__post_root_validators__)

    def constructor_call(self) -> cg.Expression:
        """The code for creating the object"""
        if self.use_construct:
            return cg.MethodCall(
                cg.Variable(self.internal_name), "construct", args=[], keywords=[cg.Keyword(cg.Variable("d"))]
            )
        else:
            return super().constructor_call()

    @staticmethod
    def _fields(clazz: Any, namespace: Namespace, use_alias_in_initializer: bool) -> Dict[str, FieldMeta]:
        clazz.update_forward_refs(**namespace.locals)
        return {
            field.name: PydanticV1FieldMeta.from_pydantic(field, use_alias_in_initializer=use_alias_in_initializer)
            for field in clazz.__fields__.values()
        }

    @staticmethod
    def applies(clz: Any) -> bool:
        try:
            pydantic = __import__("pydantic")
            if issubclass(clz, pydantic.BaseModel):
                return pydantic_version() < (2, 0, 0)
        except ImportError:
            pass
        return False

    @classmethod
    def from_clazz(cls, clazz: Any, namespace: Namespace, type_: ClassType) -> "PydanticV1ClassMeta":
        allow_population_by_field_name = getattr(clazz.Config, "allow_population_by_field_name", False)
        use_alias_in_initializer = not allow_population_by_field_name
        return cls(
            name=cast(str, clazz.__name__),
            fields=cls._fields(clazz, namespace=namespace, use_alias_in_initializer=use_alias_in_initializer),
            clazz=clazz,
            use_construct=not cls.has_validators(clazz),
        )

    @classmethod
    def only_if_set(cls, target_field: FieldMeta, source_field: FieldMeta) -> bool:
        # maintain Pydantic's unset property
        return (
            isinstance(source_field.type, OptionalFieldType)
            and isinstance(target_field.type, OptionalFieldType)
            and not target_field.required
        )

    @classmethod
    def skip_condition(cls, target_field: FieldMeta, source_field: FieldMeta) -> Optional[cg.Expression]:
        if cls.only_if_set(source_field=source_field, target_field=target_field):
            return cg.Constant(source_field.attribute_name).in_(
                cg.AttributeLookup(cg.Variable("self"), "__fields_set__")
            )
        return None
