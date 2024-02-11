from dataclass_mapper.code_generator import NONE, Expression, TernaryOperator
from dataclass_mapper.fieldtypes import FieldType, OptionalFieldType

from .expression_converter import ExpressionConverter, map_expression


class OptionalToOptionalExpressionConverter(ExpressionConverter):
    def is_applicable_to_outer(self, source: FieldType, target: FieldType) -> bool:
        return isinstance(source, OptionalFieldType) and isinstance(target, OptionalFieldType)

    def map_expression(
        self, source: FieldType, target: FieldType, source_exp: Expression, recusion_depth: int
    ) -> Expression:
        assert isinstance(source, OptionalFieldType) and isinstance(target, OptionalFieldType)
        recursive = map_expression(source.inner_type, target.inner_type, source_exp, recusion_depth + 1)
        return TernaryOperator(source_exp.is_(NONE), NONE, recursive)
