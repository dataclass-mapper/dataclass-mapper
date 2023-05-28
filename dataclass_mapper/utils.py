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


def remove_NoneType(type_: Any) -> Any:
    if is_union_type(type_):
        types = [t for t in get_args(type_) if t is not type(None)]
        assert types, "a not-none type must exist"
        type_ = types[0]
        for t in types[1:]:
            type_ = Union[type_, t]
        # type_ = Union[(t for t in get_args(real_type) if t is not type(None))]
    return type_


def is_union_subtype(type1: Any, type2: Any) -> bool:
    """return true if all of the types of the first union are also part of the second union"""
    if is_union_type(type2):
        if is_union_type(type1):
            return all(t in get_args(type2) for t in get_args(type1))
        else:
            return type1 in get_args(type2)
    else:
        return bool(type1 == type2)
