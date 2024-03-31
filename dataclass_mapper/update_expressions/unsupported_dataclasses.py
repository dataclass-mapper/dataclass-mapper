from dataclass_mapper.classmeta import is_dataclass_supported
from dataclass_mapper.code_generator import Expression, Statement
from dataclass_mapper.collection import COLLECTION
from dataclass_mapper.fieldtypes import FieldType
from dataclass_mapper.fieldtypes.class_fieldtype import ClassFieldType

from .update_expression import UpdateExpression


class UnsupportedDataclassesUpdateExpression(UpdateExpression):
    def is_applicable_to_outer(self, source: FieldType, target: FieldType) -> bool:
        return (
            isinstance(source, ClassFieldType)
            and isinstance(target, ClassFieldType)
            and is_dataclass_supported(source.cls_type)
            and is_dataclass_supported(target.cls_type)
            and not COLLECTION.contains_update(source.cls_type, target.cls_type)
        )

    def update_expression(
        self, source: FieldType, target: FieldType, source_exp: Expression, target_exp: Expression, recursion_depth: int
    ) -> Statement:
        raise TypeError(f"There is no update mapper defined between '{source}' and '{target}'.")
