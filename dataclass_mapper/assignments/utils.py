from typing import Any

from ..fieldmeta import FieldMeta


def get_var_name(fieldmeta: FieldMeta) -> str:
    return f"self.{fieldmeta.name}"


def is_mappable_to(SourceCls: Any, TargetCls: Any) -> bool:
    try:
        func_name = get_map_to_func_name(TargetCls)
        return hasattr(SourceCls, func_name)
    except TypeError:
        return False


def get_map_to_func_name(cls: Any) -> str:
    try:
        return f"_map_to_{cls.__name__}"
    except AttributeError:
        raise TypeError("Bad Type")
