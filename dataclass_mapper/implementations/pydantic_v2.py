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


class PydanticV2FieldMeta(FieldMeta):
    @classmethod
    def from_pydantic(cls, field: Any, attribute_name: str, use_alias_in_initializer: bool) -> "PydanticV2FieldMeta":
        initializer_param_name = attribute_name
        if use_alias_in_initializer:
            initializer_param_name = field.alias or attribute_name

        return cls(
            attribute_name=attribute_name,
            type=compute_field_type(field.annotation),
            required=field.is_required(),
            initializer_param_name=initializer_param_name,
            init_with_ctor=True,
        )


class PydanticV2ClassMeta(ClassMeta):
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
        vals = clazz.__pydantic_decorators__
        return (
            bool(vals.validators)
            or bool(vals.field_validators)
            or bool(vals.root_validators)
            or bool(vals.model_validators)
        )

    def constructor_call(self) -> cg.Expression:
        """The code for creating the object"""
        if self.use_construct:
            return cg.MethodCall(
                cg.Variable(self.internal_name), "model_construct", args=[], keywords=[cg.Keyword(cg.Variable("d"))]
            )
        else:
            return super().constructor_call()

    @staticmethod
    def _fields(clazz: Any, namespace: Namespace, use_alias_in_initializer: bool) -> Dict[str, FieldMeta]:
        return {
            name: PydanticV2FieldMeta.from_pydantic(field, name, use_alias_in_initializer=use_alias_in_initializer)
            for name, field in clazz.model_fields.items()
        }

    @staticmethod
    def applies(clz: Any) -> bool:
        try:
            pydantic = __import__("pydantic")
            if issubclass(clz, pydantic.BaseModel):
                return (2, 0, 0) <= pydantic_version() < (3, 0, 0)
        except ImportError:
            pass
        return False

    @classmethod
    def from_clazz(cls, clazz: Any, namespace: Namespace, type_: ClassType) -> "PydanticV2ClassMeta":
        populate_by_name = clazz.model_config.get("populate_by_name", False)
        use_alias_in_initializer = not populate_by_name
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
                cg.AttributeLookup(cg.Variable("self"), "model_fields_set")
            )
        return None
