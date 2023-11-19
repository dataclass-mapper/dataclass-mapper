from dataclass_mapper.code_generator import Expression, ListComprehension, Variable
from dataclass_mapper.fieldtypes import FieldType
from dataclass_mapper.fieldtypes.list import ListFieldType

from .expression_converter import ExpressionConverter, map_expression


class ListExpressionConverter(ExpressionConverter):
    def is_applicable_to_outer(self, source: FieldType, target: FieldType) -> bool:
        return isinstance(source, ListFieldType) and isinstance(target, ListFieldType)

    def map_expression(self, source: FieldType, target: FieldType, source_exp: Expression) -> Expression:
        assert source.inner
        source_list_element = source.inner[0]
        assert target.inner
        target_list_element = target.inner[0]
        iter_var = Variable("x")
        element_expression = map_expression(source_list_element, target_list_element, iter_var)
        return ListComprehension(element_expression, iter_var, source_exp)
