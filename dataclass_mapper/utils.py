import sys
from typing import Any, Union, get_args, get_origin


def is_union_type(type_: Any) -> bool:
    origin = get_origin(type_)
    if sys.version_info < (3, 10):
        return origin is Union
    else:
        from types import UnionType

        return origin in (Union, UnionType)


def is_optional(type_: Any) -> bool:
    # requires Python 3.8
    return is_union_type(type_) and type(None) in get_args(type_)


def is_mappable_to(SourceCls: Any, TargetCls: Any) -> bool:
    try:
        func_name = get_map_to_func_name(TargetCls)
        return hasattr(SourceCls, func_name)
    except TypeError:
        return False


def is_updatable_to(SourceCls: Any, TargetCls: Any) -> bool:
    try:
        func_name = get_mapupdate_to_func_name(TargetCls)
        return hasattr(SourceCls, func_name)
    except TypeError:
        return False


def get_map_to_func_name(cls: Any) -> str:
    try:
        identifier = f"{cls.__name__}_{id(cls)}"
        return f"_map_to_{identifier}"
    except AttributeError as exc:
        raise TypeError("Bad Type") from exc


def get_mapupdate_to_func_name(cls: Any) -> str:
    try:
        identifier = f"{cls.__name__}_{id(cls)}"
        return f"_mapupdate_to_{identifier}"
    except AttributeError as exc:
        raise TypeError("Bad Type") from exc
