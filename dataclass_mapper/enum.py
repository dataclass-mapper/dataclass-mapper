from enum import Enum
from typing import Any, Callable, Dict, Union, cast

# mapping between source members and target members
EnumMapping = Dict[Union[str, Enum], Union[str, Enum]]


def member_to_name_and_raise(
    member: Union[str, Enum], members: Dict[str, Enum], enum_cls: Any, class_description: str
) -> str:
    if isinstance(member, str) and member in members:
        return member
    if isinstance(member, enum_cls) and isinstance(member, Enum):
        return cast(str, member.name)  # in 3.11.0 .name is of type Any

    raise ValueError(
        f"The mapping key '{member}' must be a member of the {class_description} enum "
        f"'{enum_cls.__name__}' or a string with its name"
    )


def make_enum_mapper(
    mapping: EnumMapping,
    source_cls: Any,
    target_cls: Any,
) -> Callable:
    if not issubclass(source_cls, Enum) or not issubclass(target_cls, Enum):
        raise ValueError("`enum_mapper` does only support enum classes, use `mapper` for other classes")

    source_members = {member.name: member for member in source_cls}
    target_members = {member.name: member for member in target_cls}

    name_mapping: Dict[str, str] = {}
    for source_member, target_member in mapping.items():
        source_member = member_to_name_and_raise(source_member, source_members, source_cls, "source")
        target_member = member_to_name_and_raise(target_member, target_members, target_cls, "target")
        name_mapping[source_member] = target_member

    full_mapping: Dict[Any, Any] = {}
    for source_member_name, source_member in source_members.items():
        # mapping exists
        if source_member_name in name_mapping:
            full_mapping[source_member] = target_members[name_mapping[source_member_name]]
        # there's a member with the same name in the target
        elif source_member_name in target_members:
            full_mapping[source_member] = target_members[source_member_name]
        else:
            raise ValueError(
                f"The member '{source_member_name}' of the source enum '{source_cls.__name__}' doesn't have a mapping."
            )

    def convert(self: Any, extra: Dict) -> Any:
        return convert.d[self]  # type: ignore

    convert.d = full_mapping  # type: ignore

    return convert
