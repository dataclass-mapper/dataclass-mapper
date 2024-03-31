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
