from typing import Any, Dict, Optional, Tuple, cast

import dataclass_mapper.code_generator as cg
from dataclass_mapper.fieldtypes import OptionalFieldType, compute_field_type
from dataclass_mapper.implementations.utils import parse_version
from dataclass_mapper.namespace import Namespace

from .base import ClassMeta, DataclassType, FieldMeta


def pydantic_version() -> Tuple[int, int, int]:
    try:
        pydantic = __import__("pydantic")
        return parse_version(cast(str, pydantic.__version__))
    except ModuleNotFoundError:
        return (0, 0, 0)


class PydanticV2FieldMeta(FieldMeta):
    @classmethod
    def from_pydantic(cls, field: Any, name: str) -> "PydanticV2FieldMeta":
        return cls(
            name=name,
            type=compute_field_type(field.annotation),
            # allow_none=is_optional(field.annotation),
            required=field.is_required(),
            alias=field.alias,
        )


class PydanticV2ClassMeta(ClassMeta):
    _type = DataclassType.PYDANTIC

    def __init__(
        self,
        name: str,
        fields: Dict[str, FieldMeta],
        clazz: Any,
        use_construct: bool,
        populate_by_name: bool = False,
        alias_name: Optional[str] = None,
    ) -> None:
        super().__init__(name=name, fields=fields, alias_name=alias_name, clazz=clazz)
        self.use_construct = use_construct
        self.populate_by_name = populate_by_name

    @staticmethod
    def has_validators(clazz: Any) -> bool:
        vals = clazz.__pydantic_decorators__
        return (
            bool(vals.validators)
            or bool(vals.field_validators)
            or bool(vals.root_validators)
            or bool(vals.model_validators)
        )

    def return_statement(self) -> cg.Return:
        if self.use_construct:
            return cg.Return(f"{self.alias_name}.model_construct(**d)")
        else:
            return super().return_statement()

    def get_assignment_name(self, field: FieldMeta) -> str:
        if self.use_construct or self.populate_by_name:
            return field.name
        else:
            return field.alias or field.name

    @staticmethod
    def _fields(clazz: Any, namespace: Namespace) -> Dict[str, FieldMeta]:
        return {name: PydanticV2FieldMeta.from_pydantic(field, name) for name, field in clazz.model_fields.items()}

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
    def from_clazz(cls, clazz: Any, namespace: Namespace) -> "PydanticV2ClassMeta":
        return cls(
            name=cast(str, clazz.__name__),
            fields=cls._fields(clazz, namespace=namespace),
            clazz=clazz,
            use_construct=not cls.has_validators(clazz),
            populate_by_name=clazz.model_config.get("populate_by_name", False),
        )

    @classmethod
    def only_if_set(cls, source_cls: Any, target_field: FieldMeta, source_field: FieldMeta) -> bool:
        # maintain Pydantic's unset property
        return (
            isinstance(source_field.type, OptionalFieldType)
            and isinstance(target_field.type, OptionalFieldType)
            and not target_field.required
            and source_cls._type == DataclassType.PYDANTIC
        )

    @classmethod
    def post_process(
        cls, code: cg.Statement, source_cls: Any, target_field: FieldMeta, source_field: FieldMeta
    ) -> cg.Statement:
        if cls.only_if_set(source_cls=source_cls, source_field=source_field, target_field=target_field):
            code = cg.IfElse(condition=f"'{source_field.name}' in self.model_fields_set", if_block=code)
        return code
