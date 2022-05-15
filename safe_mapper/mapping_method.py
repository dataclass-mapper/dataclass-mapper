from typing import Any, get_args, get_origin

from .field import Field


class MappingMethodSourceCode:
    """Source code of the mapping method"""

    def __init__(
        self,
        source_cls: Any,
        target_cls: Any,
        actual_source_fields: dict[str, Field],
        actual_target_fields: dict[str, Field],
    ):
        self.source_cls_name = source_cls.__name__
        self.target_cls_name = target_cls.__name__
        self.actual_source_fields = actual_source_fields
        self.actual_target_fields = actual_target_fields
        self.lines = [
            f"def convert(self):",
            f"    d = {{}}",
        ]

    def _add_line(self, left_side: str, right_side: str, indent=4) -> None:
        self.lines.append(f'{" "*indent}d["{left_side}"] = {right_side}')

    def add_assignment(
        self, target_field_name: str, source_field_name: str, only_if_not_None: bool = False
    ) -> None:
        indent = 4
        if only_if_not_None:
            self.lines.append(f"    if self.{source_field_name} is not None:")
            indent = 8
        self._add_line(target_field_name, f"self.{source_field_name}", indent)

    def add_recursive(
        self, target_field_name: str, source_field_name: str, target_cls: Any, if_none: bool = False
    ) -> None:
        right_side = f"map_to(self.{source_field_name}, {target_cls.__name__})"
        if if_none:
            right_side = f"None if self.{source_field_name} is None else {right_side}"
        self._add_line(target_field_name, right_side)

    def add_recursive_list(
        self, target_field_name: str, source_field_name: str, target_cls: Any, if_none: bool = False
    ) -> None:
        right_side = f"[map_to(x, {target_cls.__name__}) for x in self.{source_field_name}]"
        if if_none:
            right_side = f"None if self.{source_field_name} is None else {right_side}"
        self._add_line(target_field_name, right_side)

    def add_mapping(self, target_field_name: str, source_field_name: str) -> None:
        source_field = self.actual_source_fields[source_field_name]
        target_field = self.actual_target_fields[target_field_name]

        # same type, just assign it
        if target_field.type == source_field.type and not (
            source_field.allow_none and target_field.disallow_none
        ):
            self.add_assignment(target_field_name, source_field_name)

        # allow optional to non-optional if target has default
        elif (
            target_field.type == source_field.type
            and source_field.allow_none
            and target_field.disallow_none
            and target_field.has_default
        ):
            self.add_assignment(target_field_name, source_field_name, only_if_not_None=True)

        # different type, buty also safe mappable
        # with optional
        elif is_mappable_to(source_field.type, target_field.type) and not (
            source_field.allow_none and target_field.disallow_none
        ):
            self.add_recursive(
                target_field_name,
                source_field_name,
                target_field.type,
                if_none=source_field.allow_none,
            )

        # both are lists of safe mappable types
        # with optional
        elif (
            get_origin(source_field.type) is list
            and get_origin(target_field.type) is list
            and is_mappable_to(get_args(source_field.type)[0], get_args(target_field.type)[0])
            and not (source_field.allow_none and target_field.disallow_none)
        ):
            self.add_recursive_list(
                target_field_name,
                source_field_name,
                get_args(target_field.type)[0],
                if_none=source_field.allow_none,
            )
        else:
            raise TypeError(
                f"{source_field} of '{self.source_cls_name}' cannot be converted to {target_field}"
            )

    def __str__(self) -> str:
        return_statement = f"    return {self.target_cls_name}(**d)"
        return "\n".join(self.lines + [return_statement])


def get_map_to_func_name(cls: Any) -> str:
    return f"_map_to_{cls.__name__}"


def is_mappable_to(SourceCls, TargetCls) -> bool:
    func_name = get_map_to_func_name(TargetCls)
    return hasattr(SourceCls, func_name)
