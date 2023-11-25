from dataclass_mapper.code_generator import Expression, ListComprehension, Variable
from dataclass_mapper.fieldtypes import FieldType
from dataclass_mapper.fieldtypes.list import ListFieldType

from .expression_converter import ExpressionConverter, map_expression


class ListExpressionConverter(ExpressionConverter):
    def is_applicable_to_outer(self, source: FieldType, target: FieldType) -> bool:
        return isinstance(source, ListFieldType) and isinstance(target, ListFieldType)

    def map_expression(
        self, source: FieldType, target: FieldType, source_exp: Expression, recursion_depth: int
    ) -> Expression:
        assert isinstance(source, ListFieldType) and isinstance(target, ListFieldType)
        iter_var = Variable(f"x{recursion_depth}")
        element_expression = map_expression(source.value_type, target.value_type, iter_var, recursion_depth + 1)
        return ListComprehension(element_expression, iter_var, source_exp)
