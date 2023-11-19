from dataclass_mapper.code_generator import Expression
from dataclass_mapper.fieldtypes import FieldType, OptionalFieldType

from .expression_converter import ExpressionConverter, map_expression


class NonOptionalToOptionalExpressionConverter(ExpressionConverter):
    def is_applicable_to_outer(self, source: FieldType, target: FieldType) -> bool:
        return not isinstance(source, OptionalFieldType) and isinstance(target, OptionalFieldType)

    def map_expression(self, source: FieldType, target: FieldType, source_exp: Expression) -> Expression:
        assert target.inner
        non_optional_target = target.inner[0]
        recursive = map_expression(source, non_optional_target, source_exp)
        return recursive
