from dataclass_mapper.code_generator import Expression
from dataclass_mapper.fieldtypes import FieldType
from dataclass_mapper.fieldtypes.class_fieldtype import ClassFieldType
from dataclass_mapper.fieldtypes.union import UnionFieldType
from dataclass_mapper.utils import is_union_subtype

from .expression_converter import ExpressionConverter


class ClassToUnionExpressionConverter(ExpressionConverter):
    def is_applicable_to_outer(self, source: FieldType, target: FieldType) -> bool:
        return (
            isinstance(source, ClassFieldType)
            and isinstance(target, UnionFieldType)
            and is_union_subtype(source.cls_type, target.inner_types)
        )

    def map_expression(self, source: FieldType, target: FieldType, source_exp: Expression) -> Expression:
        return source_exp
