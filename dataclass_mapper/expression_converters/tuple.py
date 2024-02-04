from dataclass_mapper.code_generator import Constant, DictLookup, Expression, Tuple
from dataclass_mapper.fieldtypes import FieldType
from dataclass_mapper.fieldtypes.tuple import TupleFieldType

from .expression_converter import ExpressionConverter, map_expression


class TupleExpressionConverter(ExpressionConverter):
    def is_applicable_to_outer(self, source: FieldType, target: FieldType) -> bool:
        return (
            isinstance(source, TupleFieldType)
            and isinstance(target, TupleFieldType)
            and len(source.value_types) == len(target.value_types)
        )

    def map_expression(
        self, source: FieldType, target: FieldType, source_exp: Expression, recursion_depth: int
    ) -> Expression:
        assert isinstance(source, TupleFieldType) and isinstance(target, TupleFieldType)
        return Tuple(
            [
                map_expression(s, t, DictLookup(source_exp, Constant(i)), recursion_depth + 1)
                for i, (s, t) in enumerate(zip(source.value_types, target.value_types))
            ]
        )
