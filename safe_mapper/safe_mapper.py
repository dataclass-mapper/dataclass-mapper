from dataclasses import fields
from importlib import import_module
from typing import Any, Callable, Optional, Type, TypeVar, cast


def _make_mapper(mapping: dict[str, str], source_cls: Any, target_cls: Any) -> str:
    lines = [
        f"def convert(self):",
        f"    d = {{}}",
    ]

    actual_source_fields = {field.name for field in fields(source_cls)}
    actual_target_fields = {field.name for field in fields(target_cls)}
    mapped_target_fields = set(mapping)

    for target_field, source_field in mapping.items():
        if target_field in actual_target_fields:
            lines.append(f'    d["{target_field}"] = self.{source_field}')
        else:
            raise ValueError(
                f"'{target_field}' of mapping in '{source_cls.__name__}' doesn't exist in '{target_cls.__name__}'"
            )

    # handle missing fields
    for field in actual_target_fields - mapped_target_fields:
        # default mapping: Target(x=source.x)
        if field in actual_source_fields:
            lines.append(f'    d["{field}"] = self.{field}')
        else:
            raise ValueError(
                f"'{field}' of '{target_cls.__name__}' has no mapping in '{source_cls.__name__}'"
            )

    lines.append(f"    return {target_cls.__name__}(**d)")
    return "\n".join(lines)


T = TypeVar("T")


def safe_mapper(target_cls: Any, mapping: Optional[dict[str, str]] = None) -> Callable[[T], T]:
    field_mapping = mapping or cast(dict[str, str], {})

    def wrapped(source_cls: T) -> T:
        map_code = _make_mapper(field_mapping, source_cls=source_cls, target_cls=target_cls)
        module = import_module(target_cls.__module__)

        d: dict = {}
        exec(map_code, module.__dict__, d)
        map_func = f"_map_to_{target_cls.__name__}"
        setattr(source_cls, map_func, d["convert"])

        return source_cls

    return wrapped


def map_to(obj, TargetCls: Type[T]) -> T:
    map_func = f"_map_to_{TargetCls.__name__}"
    if not hasattr(obj, map_func):
        raise NotImplementedError(
            f"Object of type '{type(obj)}' cannot be mapped to {TargetCls.__name__}'"
        )
    return cast(T, getattr(obj, map_func)())
