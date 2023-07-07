from typing import Any, Dict, Optional, cast

import dataclass_mapper.code_generator as cg
from dataclass_mapper.namespace import Namespace

from .base import ClassMeta, DataclassType, FieldMeta


class PydanticV1FieldMeta(FieldMeta):
    @classmethod
    def from_pydantic(cls, field: Any) -> "PydanticV1FieldMeta":
        return cls(
            name=field.name,
            type=field.outer_type_,
            allow_none=field.allow_none,
            required=field.required,
            alias=field.alias,
        )


class PydanticV1ClassMeta(ClassMeta):
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

    def return_statement(self) -> cg.Return:
        if self.use_construct:
            return cg.Return(f"{self.alias_name}.construct(**d)")
        else:
            return super().return_statement()

    def get_assignment_name(self, field: FieldMeta) -> str:
        if self.use_construct or self.allow_population_by_field_name:
            return field.name
        else:
            return field.alias or field.name

    @staticmethod
    def _fields(clazz: Any, namespace: Namespace) -> Dict[str, FieldMeta]:
        clazz.update_forward_refs(**namespace.locals)
        return {field.name: PydanticV1FieldMeta.from_pydantic(field) for field in clazz.__fields__.values()}

    @staticmethod
    def applies(clz: Any) -> bool:
        try:
            pydantic = __import__("pydantic")
            if issubclass(clz, pydantic.BaseModel):
                return True
        except ImportError:
            pass
        return False

    @classmethod
    def from_clazz(cls, clazz: Any, namespace: Namespace) -> "PydanticV1ClassMeta":
        return cls(
            name=cast(str, clazz.__name__),
            fields=cls._fields(clazz, namespace=namespace),
            use_construct=not cls.has_validators(clazz),
            allow_population_by_field_name=getattr(clazz.Config, "allow_population_by_field_name", False),
        )

    @classmethod
    def only_if_set(cls, source_cls: Any, target_field: FieldMeta, source_field: FieldMeta) -> bool:
        # maintain Pydantic's unset property
        return (
            source_field.allow_none
            and target_field.allow_none
            and not target_field.required
            and source_cls._type == DataclassType.PYDANTIC
        )

    @classmethod
    def post_process(
        cls, code: cg.Statement, source_cls: Any, target_field: FieldMeta, source_field: FieldMeta
    ) -> cg.Statement:
        if cls.only_if_set(source_cls=source_cls, source_field=source_field, target_field=target_field):
            code = cg.IfElse(condition=f"'{source_field.name}' in self.__fields_set__", if_block=code)
        return code
