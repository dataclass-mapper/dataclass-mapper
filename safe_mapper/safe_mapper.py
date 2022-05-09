from abc import ABCMeta
from typing import Any
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


def _check_convert(
    target_cls: Any, cls_name: str, annotations: dict, mapping: dict
) -> None:
    # check if everything is specified
    target_keys = set(mapping.keys())
    source_keys = set(mapping.values())

    actual_source_keys = set(annotations.keys())

    for key in source_keys:
        if key not in actual_source_keys:
            raise Exception(
                f"'{key}' of '{cls_name}' is not mapped to '{target_cls.__name__}'"
            )
    for key in actual_source_keys:
        if key not in source_keys:
            raise Exception(
                f"'{key}' of '{cls_name}' is not mapped to '{target_cls.__name__}'"
            )
    assert source_keys == actual_source_keys


class SafeMapper(ABCMeta):
    def __new__(mcs, name, bases, class_dict):  # type: ignore
        target_cls = class_dict["Config"].mapping_target_class
        mapping = class_dict["Config"].mapping
        annotations = class_dict["__annotations__"]

        _check_convert(target_cls, name, annotations, mapping)
        convert_code = _make_convert(mapping, target_cls)
        module = import_module(target_cls.__module__)
        exec(convert_code, module.__dict__, class_dict)

        return super().__new__(mcs, name, bases, class_dict)


def safe_convert(obj):
    return obj.convert()
