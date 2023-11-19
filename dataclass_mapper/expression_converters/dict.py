from dataclass_mapper.code_generator import (
    DictComprehension,
    Expression,
    Variable,
)
from dataclass_mapper.fieldtypes import FieldType
from dataclass_mapper.fieldtypes.dict import DictFieldType

from .expression_converter import ExpressionConverter, map_expression


class DictExpressionConverter(ExpressionConverter):
    def is_applicable_to_outer(self, source: FieldType, target: FieldType) -> bool:
        return isinstance(source, DictFieldType) and isinstance(target, DictFieldType)

    def map_expression(self, source: FieldType, target: FieldType, source_exp: Expression) -> Expression:
        assert source.inner and len(source.inner) == 2
        source_key = source.inner[0]
        source_value = source.inner[1]
        assert target.inner and len(target.inner) == 2
        target_key = target.inner[0]
        target_value = target.inner[1]
        key_var = Variable("k")
        value_var = Variable("v")
        key_mapping_expression = map_expression(source_key, target_key, key_var)
        value_mapping_expression = map_expression(source_value, target_value, value_var)
        return DictComprehension(key_mapping_expression, value_mapping_expression, key_var, value_var, source_exp)
