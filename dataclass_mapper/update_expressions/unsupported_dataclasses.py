from dataclass_mapper.classmeta import is_dataclass_supported
from dataclass_mapper.code_generator import Expression, MethodCall, Variable
from dataclass_mapper.fieldtypes import FieldType
from dataclass_mapper.fieldtypes.class_fieldtype import ClassFieldType
from dataclass_mapper.utils import get_mapupdate_to_func_name, is_updatable_to

from .update_expression import UpdateExpression


class UnsupportedDataclassesUpdateExpression(UpdateExpression):
    def is_applicable_to_outer(self, source: FieldType, target: FieldType) -> bool:
        return (
            isinstance(source, ClassFieldType)
            and isinstance(target, ClassFieldType)
            and is_dataclass_supported(source.cls_type)
            and is_dataclass_supported(target.cls_type)
            and not is_updatable_to(source.cls_type, target.cls_type)
        )

    def update_expression(
        self, source: FieldType, target: FieldType, source_exp: Expression, target_exp: Expression, recursion_depth: int
    ) -> Expression:
        # TODO: write better message
        raise TypeError("Updating between is not possible")
