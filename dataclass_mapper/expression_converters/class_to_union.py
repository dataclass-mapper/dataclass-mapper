from dataclass_mapper.code_generator import Expression
from dataclass_mapper.fieldtypes import FieldType
from dataclass_mapper.fieldtypes.class_fieldtype import ClassFieldType
from dataclass_mapper.fieldtypes.union import UnionFieldType

from .expression_converter import ExpressionConverter


class ClassToUnionExpressionConverter(ExpressionConverter):
    def is_applicable_to_outer(self, source: FieldType, target: FieldType) -> bool:
        return (
            isinstance(source, ClassFieldType) and isinstance(target, UnionFieldType) and source in target.inner_types
        )

    def map_expression(
        self, source: FieldType, target: FieldType, source_exp: Expression, recursion_depth: int
    ) -> Expression:
        return source_exp
