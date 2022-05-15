from dataclasses import dataclass
from typing import Any, Callable, Union, get_args, get_origin
from uuid import uuid4

from .field import Field


@dataclass
class Default:
    value: Any


@dataclass
class DefaultFactory:
    factory: Callable[[Any], Any]


Origin = Union[str, Default, DefaultFactory]


class MappingMethodSourceCode:
    """Source code of the mapping method"""

    def __init__(
        self,
        source_cls: Any,
        target_cls: Any,
        actual_source_fields: dict[str, Field],
        actual_target_fields: dict[str, Field],
        from_classmethod: bool,
    ):
        self.source_cls_name = source_cls.__name__
        self.target_cls_name = target_cls.__name__
        self.actual_source_fields = actual_source_fields
        self.actual_target_fields = actual_target_fields
        self.from_classmethod = from_classmethod
        if self.from_classmethod:
            self.lines = [
                f"@classmethod",
                f'def convert(cls, obj: {self.source_cls_name}) -> "{self.target_cls_name}":',
                f"    d = {{}}",
            ]
        else:
            self.lines = [
                f'def convert(self) -> "{self.target_cls_name}":',
                f"    d = {{}}",
            ]
        self.factories: dict[str, Callable] = {}

    def get_source(self, name: str) -> str:
        if self.from_classmethod:
            return f"obj.{name}"
        else:
            return f"self.{name}"

    def _add_line(self, left_side: str, right_side: str, indent=4) -> None:
        self.lines.append(f'{" "*indent}d["{left_side}"] = {right_side}')

    def add_assignment(
        self, target_field_name: str, source_field_name: str, only_if_not_None: bool = False
    ) -> None:
        source = self.get_source(source_field_name)
        indent = 4
        if only_if_not_None:
            self.lines.append(f"    if {source} is not None:")
            indent = 8
        self._add_line(target_field_name, source, indent)

    def _get_map_func(self, name: str, target_cls: Any) -> str:
        if self.from_classmethod:
            func_name = get_map_from_func_name(target_cls)
            return f"{target_cls.__name__}.{func_name}({name})"
        else:
            func_name = get_map_to_func_name(target_cls)
            return f"{name}.{func_name}()"

    def add_recursive(
        self, target_field_name: str, source_field_name: str, target_cls: Any, if_none: bool = False
    ) -> None:
        source = self.get_source(source_field_name)

        right_side = self._get_map_func(source, target_cls)
        if if_none:
            right_side = f"None if {source} is None else {right_side}"
        self._add_line(target_field_name, right_side)

    def add_recursive_list(
        self,
        target_field_name: str,
        source_field_name: str,
        target_cls: Any,
        if_none: bool = False,
        only_if_not_None: bool = False,
    ) -> None:
        source = self.get_source(source_field_name)
        right_side = f'[{self._get_map_func("x", target_cls)} for x in {source}]'
        if if_none:
            right_side = f"None if {source} is None else {right_side}"
        indent = 4

        if only_if_not_None:
            self.lines.append(f"    if {source} is not None:")
            indent = 8
        self._add_line(target_field_name, right_side, indent)

    def add_default(self, target_field_name: str, default: Default) -> None:
        self._add_line(target_field_name, default.value)

    def add_default_factory(self, target_field_name: str, default_factory: DefaultFactory) -> None:
        name = f"_{uuid4().hex}"
        self.factories[name] = default_factory.factory
        source = self.get_source(name)
        self._add_line(target_field_name, f"{source}()")

    def add_mapping(self, target_field_name: str, source_origin: Origin) -> None:
        if isinstance(source_origin, Default):
            self.add_default(target_field_name, source_origin)
        elif isinstance(source_origin, DefaultFactory):
            self.add_default_factory(target_field_name, source_origin)
        else:
            source_field_name: str = source_origin

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

            # allow optional to non-optional if target has default
            elif (
                get_origin(source_field.type) is list
                and get_origin(target_field.type) is list
                and is_mappable_to(get_args(source_field.type)[0], get_args(target_field.type)[0])
                and source_field.allow_none
                and target_field.disallow_none
                and target_field.has_default
            ):
                self.add_recursive_list(
                    target_field_name,
                    source_field_name,
                    get_args(target_field.type)[0],
                    if_none=source_field.allow_none,
                    only_if_not_None=True,
                )

            # impossible
            else:
                raise TypeError(
                    f"{source_field} of '{self.source_cls_name}' cannot be converted to {target_field}"
                )

    def __str__(self) -> str:
        if self.from_classmethod:
            return_statement = f"    return cls(**d)"
        else:
            return_statement = f"    return {self.target_cls_name}(**d)"
        return "\n".join(self.lines + [return_statement])


def get_map_to_func_name(cls: Any) -> str:
    return f"_map_to_{cls.__name__}"


def get_map_from_func_name(cls: Any) -> str:
    return f"_map_from_{cls.__name__}"


def is_mappable_to(SourceCls, TargetCls) -> bool:
    func_name = get_map_to_func_name(TargetCls)
    return hasattr(SourceCls, func_name)
