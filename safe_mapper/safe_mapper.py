from dataclasses import fields
from importlib import import_module
from typing import Any, Callable, Optional, Type, TypeVar, cast


def _make_mapper(mapping: dict[str, str], source_cls: Any, target_cls: Any) -> str:
    lines = [
        f"def convert(self):",
        f"    d = {{}}",
    ]

    actual_source_fields = {field.name: field for field in fields(source_cls)}
    actual_target_fields = {field.name: field for field in fields(target_cls)}
    mapped_target_fields = set(mapping)

    for target_field, source_field in mapping.items():
        if target_field in actual_target_fields:
            source_type = actual_source_fields[source_field].type
            target_type = actual_target_fields[target_field].type
            if is_mappable_to(source_type, target_type):
                lines.append(
                    f'    d["{target_field}"] = map_to(self.{source_field}, {target_type.__name__})'
                )
            else:
                lines.append(f'    d["{target_field}"] = self.{source_field}')
        else:
            raise ValueError(
                f"'{target_field}' of mapping in '{source_cls.__name__}' doesn't exist in '{target_cls.__name__}'"
            )

    # handle missing fields
    for field in actual_target_fields.keys() - mapped_target_fields:
        if field in actual_source_fields:
            source_type = actual_source_fields[field].type
            target_type = actual_target_fields[field].type
            if is_mappable_to(source_type, target_type):
                lines.append(f'    d["{field}"] = map_to(self.{field}, {target_type.__name__})')
            else:
                lines.append(f'    d["{field}"] = self.{field}')
        else:
            raise ValueError(
                f"'{field}' of '{target_cls.__name__}' has no mapping in '{source_cls.__name__}'"
            )

    lines.append(f"    return {target_cls.__name__}(**d)")
    return "\n".join(lines)


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
