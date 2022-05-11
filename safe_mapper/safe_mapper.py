from abc import ABCMeta
from typing import Any, TypeVar, Type
from dataclasses import fields
from importlib import import_module


def _make_convert(mapping: dict, target_cls):
    lines = [
        f"def convert(self):",
        f"    d = {{}}",
    ]

    for target_key, source_key in mapping.items():
        lines.append(f'    d["{target_key}"] = self.{source_key}')
    lines.append(f"    return {target_cls.__name__}(**d)")
    return "\n".join(lines)


def _check_convert(target_cls: Any, source_cls: Any, mapping: dict) -> None:
    # check if everything is specified
    target_keys = set(mapping.keys())

    actual_target_keys = {field.name for field in fields(target_cls)}

    for key in target_keys:
        if key not in actual_target_keys:
            raise ValueError(
                f"'{key}' of mapping in '{source_cls.__name__}' doesn't exist in '{target_cls.__name__}'"
            )
    for key in actual_target_keys:
        if key not in target_keys:
            raise ValueError(
                f"'{key}' of '{target_cls.__name__}' has no mapping in '{source_cls.__name__}'"
            )
    assert target_keys == actual_target_keys


T = TypeVar("T")


def safe_mapper(source_cls: Type[T]) -> Type[T]:
    target_cls = source_cls.Config.mapping_target_class
    mapping = source_cls.Config.mapping

    _check_convert(target_cls, source_cls, mapping)
    convert_code = _make_convert(mapping, target_cls)
    module = import_module(target_cls.__module__)

    d = {}
    exec(convert_code, module.__dict__, d)
    source_cls.convert = d["convert"]

    return source_cls


def safe_convert(obj):
    return obj.convert()
