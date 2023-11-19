from dataclass_mapper.code_generator import Expression
from dataclass_mapper.fieldtypes import FieldType
from dataclass_mapper.fieldtypes.class_fieldtype import ClassFieldType

from .expression_converter import ExpressionConverter


class SameClassExpressionConverter(ExpressionConverter):
    def is_applicable_to_outer(self, source: FieldType, target: FieldType) -> bool:
        return (
            isinstance(source, ClassFieldType) and isinstance(target, ClassFieldType) and source._type is target._type
        )

    def map_expression(self, source: FieldType, target: FieldType, source_exp: Expression) -> Expression:
        return source_exp
