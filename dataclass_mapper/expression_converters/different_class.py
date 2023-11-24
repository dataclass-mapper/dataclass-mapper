from dataclass_mapper.code_generator import Expression, MethodCall, Variable
from dataclass_mapper.fieldtypes import FieldType
from dataclass_mapper.fieldtypes.class_fieldtype import ClassFieldType
from dataclass_mapper.utils import get_map_to_func_name, is_mappable_to

from .expression_converter import ExpressionConverter


class DifferentClassExpressionConverter(ExpressionConverter):
    def is_applicable_to_outer(self, source: FieldType, target: FieldType) -> bool:
        return (
            isinstance(source, ClassFieldType)
            and isinstance(target, ClassFieldType)
            and source.cls_type is not target.cls_type
            and is_mappable_to(source.cls_type, target.cls_type)
        )

    def map_expression(self, source: FieldType, target: FieldType, source_exp: Expression) -> Expression:
        assert isinstance(target, ClassFieldType)
        extra_variable = Variable("extra")
        return MethodCall(source_exp, get_map_to_func_name(target.cls_type), [extra_variable])
