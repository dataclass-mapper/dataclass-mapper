from dataclass_mapper.code_generator import Expression, SetComprehension, Variable
from dataclass_mapper.fieldtypes import FieldType, SetFieldType

from .expression_converter import ExpressionConverter, map_expression


class SetExpressionConverter(ExpressionConverter):
    def is_applicable_to_outer(self, source: FieldType, target: FieldType) -> bool:
        return isinstance(source, SetFieldType) and isinstance(target, SetFieldType)

    def map_expression(
        self, source: FieldType, target: FieldType, source_exp: Expression, recursion_depth: int
    ) -> Expression:
        assert isinstance(source, SetFieldType) and isinstance(target, SetFieldType)
        iter_var = Variable(f"x{recursion_depth}")
        element_expression = map_expression(source.value_type, target.value_type, iter_var, recursion_depth + 1)
        return SetComprehension(element_expression, iter_var, source_exp)
