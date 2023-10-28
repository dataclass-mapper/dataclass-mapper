import warnings
from copy import copy
from typing import Any, Dict

from .mapping_method import (
    CurrentStringFieldMapping,
    FieldMeta,
    Ignore,
    Spezial,
    StringFieldMapping,
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
    normalized_mapping: CurrentStringFieldMapping = dict()

    for target_field_name, raw_source in mapping.items():
        if isinstance(raw_source, Spezial):
            if raw_source is Spezial.USE_DEFAULT or raw_source is Spezial.IGNORE_MISSING_MAPPING:
                warnings.warn(
                    f"{raw_source.name} is deprecated, use init_with_default() instead",
                    DeprecationWarning,
                )
                normalized_mapping[target_field_name] = Ignore(created_via=raw_source.name)
            else:
                assert False, "only those two values are possible"

        else:
            normalized_mapping[target_field_name] = raw_source

    return normalized_mapping
