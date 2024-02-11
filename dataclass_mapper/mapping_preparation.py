import warnings
from copy import copy
from typing import Any, Dict

from .implementations.base import ClassMeta, FieldMeta
from .implementations.sqlalchemy import InstrumentedAttribute, extract_instrumented_attribute_name_and_class
from .special_field_mappings import (
    CurrentStringFieldMapping,
    Ignore,
    Origin,
    Spezial,
    StringFieldMapping,
    StringSqlAlchemyFieldMapping,
)


def generate_missing_mappings(
    mapping: StringFieldMapping,
    actual_source_fields: Dict[str, FieldMeta],
    actual_target_fields: Dict[str, FieldMeta],
) -> StringFieldMapping:
    """Generate a full mappings list, extended with the mappings that are defined implicitely."""
    extended_mapping = copy(mapping)

    for target_field_name in actual_target_fields:
        if target_field_name not in mapping and target_field_name in actual_source_fields:
            extended_mapping[target_field_name] = target_field_name

    return extended_mapping


def raise_if_mapping_doesnt_match_target(
    mapping: StringFieldMapping,
    source_cls: Any,
    target_cls: Any,
    actual_target_fields: Dict[str, FieldMeta],
) -> None:
    """Check the mappings target list matches the target class field list."""

    for target_field_name in actual_target_fields:
        if target_field_name not in mapping:
            raise ValueError(
                f"'{target_field_name}' of '{target_cls.__name__}' has no mapping in '{source_cls.__name__}'"
            )

    for target_field_name in mapping:
        if target_field_name not in actual_target_fields:
            raise ValueError(
                f"'{target_field_name}' of mapping in '{source_cls.__name__}' doesn't exist in '{target_cls.__name__}'"
            )


def normalize_deprecated_mappings(mapping: StringFieldMapping) -> CurrentStringFieldMapping:
    """Replace the deprecated options with their modern counterparts."""
    normalized_mapping: CurrentStringFieldMapping = {}

    for target_field_name, raw_source in mapping.items():
        if isinstance(raw_source, Spezial):
            if raw_source is Spezial.USE_DEFAULT or raw_source is Spezial.IGNORE_MISSING_MAPPING:
                warnings.warn(
                    f"{raw_source.name} is deprecated, use init_with_default() instead",
                    DeprecationWarning,
                    stacklevel=1,
                )
                normalized_mapping[target_field_name] = Ignore(created_via=raw_source.name)
            else:
                raise AssertionError("only those two values are possible")

        else:
            normalized_mapping[target_field_name] = raw_source

    return normalized_mapping


def convert_sqlalchemy_fields(
    mapping: StringSqlAlchemyFieldMapping, source_cls_meta: ClassMeta, target_cls_meta: ClassMeta
) -> StringFieldMapping:
    """Replace the SqlAlchemy custom field types with their field names."""
    new_mapping: StringFieldMapping = {}

    for target_field_name, raw_source in mapping.items():
        new_target_field_name: str

        if isinstance(target_field_name, InstrumentedAttribute):
            name, clazz = extract_instrumented_attribute_name_and_class(target_field_name)
            if clazz != target_cls_meta.clazz:
                raise ValueError(
                    f"The target field '{name}' in the mapping doesn't belong "
                    f"to target class '{target_cls_meta.name}'."
                )
            new_target_field_name = name
        else:
            new_target_field_name = target_field_name

        new_raw_source: Origin
        if isinstance(raw_source, InstrumentedAttribute):
            name, clazz = extract_instrumented_attribute_name_and_class(raw_source)
            if clazz != source_cls_meta.clazz:
                raise ValueError(
                    f"The source field '{name}' in the mapping doesn't belong "
                    f"to source class '{source_cls_meta.name}'."
                )
            new_raw_source = name
        else:
            new_raw_source = raw_source

        new_mapping[new_target_field_name] = new_raw_source

    return new_mapping
