import sys
from dataclasses import dataclass
from inspect import isfunction, signature
from typing import Any, Callable, Dict, Optional, Type, Union, cast, get_args, get_origin, get_type_hints

from dataclass_mapper.namespace import Namespace

CallableWithMax1Parameter = Union[Callable[[], Any], Callable[[Any], Any]]


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


@dataclass
class TypeAnnotation:
    first_param_type: Optional[Type]
    return_type: Optional[Type]


def extract_function_types(
    callable: CallableWithMax1Parameter, namespace: Optional[Namespace] = None
) -> TypeAnnotation:
    """extracts the type of the only parameter (if there is one at all), and the type of the return value"""

    if not isfunction(callable):
        callable = callable.__call__  # type: ignore[operator]

    params = list(signature(callable).parameters.values())
    type_hints: Dict[str, Any]
    try:
        type_hints = (
            get_type_hints(callable, globalns=namespace.globals, localns=namespace.locals)
            if namespace
            else get_type_hints(callable)
        )
    except NameError:
        type_hints = {}

    first_param_type: Optional[Type] = None
    if params:
        first_param = params[0]
        first_param_type = type_hints.get(first_param.name)
    return_type: Optional[Type] = type_hints.get("return")

    return TypeAnnotation(first_param_type=first_param_type, return_type=return_type)


def get_class_name(cls: Any) -> str:
    try:
        return cast(str, cls.__name__)
    except AttributeError:
        return str(cls)
