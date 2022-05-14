from dataclasses import Field, fields
from importlib import import_module
from typing import Any, Callable, Optional, Type, TypeVar, cast


class MappingFunction:
    def __init__(
        self,
        target_cls: Any,
        actual_source_fields: dict[str, Field],
        actual_target_fields: dict[str, Field],
    ):
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
        self, target_field_name: str, source_field_name: str, target_cls: Any
    ) -> None:
        self._add_line(
            target_field_name, f"map_to(self.{source_field_name}, {target_cls.__name__})"
        )

    def add_mapping(self, target_field_name: str, source_field_name: str) -> None:
        source_type = self.actual_source_fields[source_field_name].type
        target_type = self.actual_target_fields[target_field_name].type
        if is_mappable_to(source_type, target_type):
            self.add_recursive(target_field_name, source_field_name, target_type)
        else:
            self.add_assignment(target_field_name, source_field_name)

    def __str__(self) -> str:
        return_statement = f"    return {self.target_cls_name}(**d)"
        return "\n".join(self.lines + [return_statement])


def _make_mapper(mapping: dict[str, str], source_cls: Any, target_cls: Any) -> str:
    actual_source_fields = {field.name: field for field in fields(source_cls)}
    actual_target_fields = {field.name: field for field in fields(target_cls)}
    mapping_func = MappingFunction(
        target_cls,
        actual_source_fields=actual_source_fields,
        actual_target_fields=actual_target_fields,
    )
    mapped_target_fields = set(mapping)

    for target_field, source_field in mapping.items():
        if target_field in actual_target_fields:
            mapping_func.add_mapping(target_field, source_field)
        else:
            raise ValueError(
                f"'{target_field}' of mapping in '{source_cls.__name__}' doesn't exist in '{target_cls.__name__}'"
            )

    # handle missing fields
    for field in actual_target_fields.keys() - mapped_target_fields:
        if field in actual_source_fields:
            mapping_func.add_mapping(field, field)
        else:
            raise ValueError(
                f"'{field}' of '{target_cls.__name__}' has no mapping in '{source_cls.__name__}'"
            )

    return str(mapping_func)


def get_map_to_func_name(cls: Any) -> str:
    return f"_map_to_{cls.__name__}"


def is_mappable_to(SourceCls, TargetCls) -> bool:
    func_name = get_map_to_func_name(TargetCls)
    return hasattr(SourceCls, func_name)


T = TypeVar("T")


def safe_mapper(target_cls: Any, mapping: Optional[dict[str, str]] = None) -> Callable[[T], T]:
    field_mapping = mapping or cast(dict[str, str], {})

    def wrapped(source_cls: T) -> T:
        map_code = _make_mapper(field_mapping, source_cls=source_cls, target_cls=target_cls)
        module = import_module(target_cls.__module__)

        d: dict = {}
        exec(map_code, module.__dict__, d)
        setattr(source_cls, get_map_to_func_name(target_cls), d["convert"])

        return source_cls

    return wrapped


def map_to(obj, TargetCls: Type[T]) -> T:
    func_name = get_map_to_func_name(TargetCls)
    if not hasattr(obj, func_name):
        raise NotImplementedError(
            f"Object of type '{type(obj)}' cannot be mapped to {TargetCls.__name__}'"
        )
    return cast(T, getattr(obj, func_name)())
