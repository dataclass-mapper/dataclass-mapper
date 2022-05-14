from typing import Any

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

    def _add_line(self, left_side: str, right_side: str) -> None:
        self.lines.append(f'    d["{left_side}"] = {right_side}')

    def add_assignment(self, target_field_name: str, source_field_name: str) -> None:
        self._add_line(target_field_name, f"self.{source_field_name}")

    def add_recursive(
        self, target_field_name: str, source_field_name: str, target_cls: Any, if_none: bool = False
    ) -> None:
        right_side = f"map_to(self.{source_field_name}, {target_cls.__name__})"
        if if_none:
            right_side = f"None if self.{source_field_name} is None else {right_side}"
        self._add_line(target_field_name, right_side)

    def add_mapping(self, target_field_name: str, source_field_name: str) -> None:
        source_field = self.actual_source_fields[source_field_name]
        target_field = self.actual_target_fields[target_field_name]
        if target_field.type == source_field.type and not (
            source_field.allow_none and target_field.disallow_none
        ):
            self.add_assignment(target_field_name, source_field_name)
        elif is_mappable_to(source_field.type, target_field.type) and not (
            source_field.allow_none and target_field.disallow_none
        ):
            self.add_recursive(
                target_field_name,
                source_field_name,
                target_field.type,
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
