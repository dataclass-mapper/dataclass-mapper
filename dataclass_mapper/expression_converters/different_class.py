from dataclass_mapper.code_generator import Constant, DictLookup, Expression, FunctionCall, Variable
from dataclass_mapper.collection import COLLECTION
from dataclass_mapper.fieldtypes import FieldType
from dataclass_mapper.fieldtypes.class_fieldtype import ClassFieldType

from .expression_converter import ExpressionConverter


class DifferentClassExpressionConverter(ExpressionConverter):
    def is_applicable_to_outer(self, source: FieldType, target: FieldType) -> bool:
        return (
            isinstance(source, ClassFieldType)
            and isinstance(target, ClassFieldType)
            and source.cls_type is not target.cls_type
            and COLLECTION.contains_create(source.cls_type, target.cls_type)
        )

    def map_expression(
        self, source: FieldType, target: FieldType, source_exp: Expression, recursion_depth: int
    ) -> Expression:
        assert isinstance(source, ClassFieldType)
        assert isinstance(target, ClassFieldType)
        extra_variable = Variable("extra")
        func_name = COLLECTION.create_func_name(source.cls_type, target.cls_type)
        function = DictLookup(Variable("COLLECTION"), Constant(func_name))
        return FunctionCall(function, [source_exp, extra_variable])
