from enum import Enum
from typing import Any, Callable, cast

# mapping between source members and target members
EnumMapping = dict[str, str]


def make_enum_mapper(
    mapping: EnumMapping,
    source_cls: Any,
    target_cls: Any,
) -> Callable:
    assert issubclass(source_cls, Enum)
    assert issubclass(target_cls, Enum)

    source_members = {member.name: member for member in source_cls}
    target_members = {member.name: member for member in target_cls}

    if unknown_source_members := set(mapping.keys()) - set(source_members.keys()):
        unknown = list(unknown_source_members)[0]
        raise ValueError(
            f"The mapping key '{unknown}' is not part of the source enum '{source_cls.__name__}'"
        )
    if unknown_target_members := set(mapping.values()) - set(target_members.keys()):
        unknown = list(unknown_target_members)[0]
        raise ValueError(
            f"The mapping key '{unknown}' is not part of the target enum '{target_cls.__name__}'"
        )

    full_mapping: dict[Any, Any] = {}
    for source_member_name, source_member in source_members.items():
        # mapping exists
        if source_member_name in mapping:
            full_mapping[source_member] = target_members[mapping[source_member.name]]
        # there's a member with the same name in the target
        elif source_member_name in target_members:
            full_mapping[source_member] = target_members[source_member_name]
        else:
            raise ValueError(
                f"The member '{source_member_name}' of the source enum '{source_cls.__name__}' doesn't have a mapping."
            )

    def convert(self: Any) -> Any:
        return convert.d[self]  # type: ignore

    convert.d = full_mapping  # type: ignore

    return convert
