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
        assert isinstance(source, DictFieldType) and isinstance(target, DictFieldType)
        key_var = Variable("k")
        value_var = Variable("v")
        key_mapping_expression = map_expression(source.key_type, target.key_type, key_var)
        value_mapping_expression = map_expression(source.value_type, target.value_type, value_var)
        return DictComprehension(key_mapping_expression, value_mapping_expression, key_var, value_var, source_exp)
