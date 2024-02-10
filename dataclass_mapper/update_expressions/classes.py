from dataclass_mapper.code_generator import Expression, ExpressionStatement, MethodCall, Statement, Variable
from dataclass_mapper.fieldtypes import FieldType
from dataclass_mapper.fieldtypes.class_fieldtype import ClassFieldType
from dataclass_mapper.utils import get_mapupdate_to_func_name, is_updatable_to

from .update_expression import UpdateExpression


class ClassesUpdateExpression(UpdateExpression):
    def is_applicable_to_outer(self, source: FieldType, target: FieldType) -> bool:
        return (
            isinstance(source, ClassFieldType)
            and isinstance(target, ClassFieldType)
            and is_updatable_to(source.cls_type, target.cls_type)
        )

    def update_expression(
        self, source: FieldType, target: FieldType, source_exp: Expression, target_exp: Expression, recursion_depth: int
    ) -> Statement:
        assert isinstance(target, ClassFieldType)
        extra_variable = Variable("extra")
        return ExpressionStatement(
            MethodCall(source_exp, get_mapupdate_to_func_name(target.cls_type), [target_exp, extra_variable])
        )
