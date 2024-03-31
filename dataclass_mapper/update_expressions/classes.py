from dataclass_mapper.code_generator import (
    Constant,
    DictLookup,
    Expression,
    ExpressionStatement,
    FunctionCall,
    Statement,
    Variable,
)
from dataclass_mapper.collection import COLLECTION
from dataclass_mapper.fieldtypes import FieldType
from dataclass_mapper.fieldtypes.class_fieldtype import ClassFieldType

from .update_expression import UpdateExpression


class ClassesUpdateExpression(UpdateExpression):
    def is_applicable_to_outer(self, source: FieldType, target: FieldType) -> bool:
        return (
            isinstance(source, ClassFieldType)
            and isinstance(target, ClassFieldType)
            and COLLECTION.contains_update(source.cls_type, target.cls_type)
        )

    def update_expression(
        self, source: FieldType, target: FieldType, source_exp: Expression, target_exp: Expression, recursion_depth: int
    ) -> Statement:
        assert isinstance(source, ClassFieldType)
        assert isinstance(target, ClassFieldType)
        extra_variable = Variable("extra")
        func_name = COLLECTION.update_func_name(source.cls_type, target.cls_type)
        function = DictLookup(Variable("COLLECTION"), Constant(func_name))
        return ExpressionStatement(FunctionCall(function, [source_exp, target_exp, extra_variable]))
