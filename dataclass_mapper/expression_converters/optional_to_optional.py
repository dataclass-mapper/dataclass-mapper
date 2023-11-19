from dataclass_mapper.code_generator import NONE, Expression, TernaryOperator
from dataclass_mapper.fieldtypes import FieldType, OptionalFieldType

from .expression_converter import ExpressionConverter, map_expression


class OptionalToOptionalExpressionConverter(ExpressionConverter):
    def is_applicable_to_outer(self, source: FieldType, target: FieldType) -> bool:
        return isinstance(source, OptionalFieldType) and isinstance(target, OptionalFieldType)

    def map_expression(self, source: FieldType, target: FieldType, source_exp: Expression) -> Expression:
        assert source.inner
        non_optional_source = source.inner[0]
        assert target.inner
        non_optional_target = target.inner[0]
        recursive = map_expression(non_optional_source, non_optional_target, source_exp)
        return TernaryOperator(source_exp.equals(NONE), NONE, recursive)
