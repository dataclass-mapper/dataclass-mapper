from dataclass_mapper.code_generator import Expression
from dataclass_mapper.fieldtypes import FieldType
from dataclass_mapper.fieldtypes.union import UnionFieldType
from dataclass_mapper.utils import is_union_subtype

from .expression_converter import ExpressionConverter


class UnionToUnionExpressionConverter(ExpressionConverter):
    def is_applicable_to_outer(self, source: FieldType, target: FieldType) -> bool:
        return (
            isinstance(source, UnionFieldType)
            and isinstance(target, UnionFieldType)
            and is_union_subtype(source.inner_types, target.inner_types)
        )

    def map_expression(self, source: FieldType, target: FieldType, source_exp: Expression) -> Expression:
        return source_exp
