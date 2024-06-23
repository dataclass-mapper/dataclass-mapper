from typing import Any

from .base import FieldType
from .not_supported import NotSupportedFieldType


def compute_field_type(type_: Any) -> FieldType:
    for field_type in FieldType.all_field_types:
        if field_type.is_applicable(type_):
            return field_type.from_type(type_)

    return NotSupportedFieldType.from_type(type_)
