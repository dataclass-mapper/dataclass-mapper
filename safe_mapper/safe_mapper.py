from dataclasses import fields, is_dataclass
from importlib import import_module
from typing import Any, Callable, Optional, Type, TypeVar, cast

from .field import Field
from .mapping_method import (
    MappingMethodSourceCode,
    Origin,
    get_map_from_func_name,
    get_map_to_func_name,
)


def get_class_fields(cls: Any) -> dict[str, Field]:
    if is_dataclass(cls):
        return {field.name: Field.from_dataclass(field) for field in fields(cls)}
    try:
        pydantic = __import__("pydantic")
        if issubclass(cls, pydantic.BaseModel):
            return {field.name: Field.from_pydantic(field) for field in cls.__fields__.values()}
    except ImportError:
        pass
    raise NotImplementedError("only dataclasses and pydantic classes are supported")


def _make_mapper(
    mapping: dict[str, Origin],
    source_cls: Any,
    target_cls: Any,
    from_classmethod: bool = False,
) -> str:
    actual_source_fields = get_class_fields(source_cls)
    actual_target_fields = get_class_fields(target_cls)
    source_code = MappingMethodSourceCode(
        source_cls=source_cls,
        target_cls=target_cls,
        actual_source_fields=actual_source_fields,
        actual_target_fields=actual_target_fields,
        from_classmethod=from_classmethod,
    )

    for target_field_name in actual_target_fields.keys():
        # mapping exists
        if target_field_name in mapping:
            source_code.add_mapping(
                target_field_name=target_field_name,
                source_origin=mapping[target_field_name],
            )
        # there's a variable with the same name in the source
        elif target_field_name in actual_source_fields:
            source_code.add_mapping(
                target_field_name=target_field_name,
                source_origin=target_field_name,
            )
        # target has some defaults, so a mapping is not necessary
        elif actual_target_fields[target_field_name].has_default:
            pass
        # not possible to map
        else:
            raise ValueError(
                f"'{target_field_name}' of '{target_cls.__name__}' has no mapping in '{source_cls.__name__}'"
            )

    for target_field_name in mapping.keys() - actual_target_fields.keys():
        raise ValueError(
            f"'{target_field_name}' of mapping in '{source_cls.__name__}' doesn't exist in '{target_cls.__name__}'"
        )

    return str(source_code)


T = TypeVar("T")


def safe_mapper(TargetCls: Any, mapping: Optional[dict[str, Origin]] = None) -> Callable[[T], T]:
    """Adds a private mapper method to the class, that maps the current class to the `TargetCls`.
    The mapper method can be called using the `map_to` function.

    With the `mapping` parameter you can additionally define attribute name changes, in the format `dict[TargetName, SourceName]`.
    """
    field_mapping = mapping or cast(dict[str, Origin], {})

    def wrapped(source_cls: T) -> T:
        map_code = _make_mapper(field_mapping, source_cls=source_cls, target_cls=TargetCls)
        module = import_module(TargetCls.__module__)

        d: dict = {}
        exec(map_code, module.__dict__, d)
        setattr(source_cls, get_map_to_func_name(TargetCls), d["convert"])

        return source_cls

    return wrapped


def safe_mapper_from(
    SourceCls: Any, mapping: Optional[dict[str, Origin]] = None
) -> Callable[[T], T]:
    """Adds a private mapper method to the class, that maps an object of `SourceCls` to the current class.
    The mapper method can be called using the `map_to` function.

    With the `mapping` parameter you can additionally define attribute name changes, in the format `dict[TargetName, SourceName]`.
    """
    field_mapping = mapping or cast(dict[str, Origin], {})

    def wrapped(target_cls: T) -> T:
        map_code = _make_mapper(
            field_mapping,
            source_cls=SourceCls,
            target_cls=target_cls,
            from_classmethod=True,
        )
        module = import_module(SourceCls.__module__)

        d: dict = {}
        print(map_code)
        exec(map_code, module.__dict__, d)
        setattr(target_cls, get_map_from_func_name(SourceCls), d["convert"])

        return target_cls

    return wrapped


def map_to(obj, TargetCls: Type[T]) -> T:
    """Maps the given object to an object of type `TargetCls`, if such a safe mapping was defined for the type of the given object."""
    func_name = get_map_to_func_name(TargetCls)
    if hasattr(obj, func_name):
        return cast(T, getattr(obj, func_name)())

    func_name_from = get_map_from_func_name(type(obj))
    if hasattr(TargetCls, func_name_from):
        return cast(T, getattr(TargetCls, func_name_from)(obj))

    raise NotImplementedError(
        f"Object of type '{type(obj)}' cannot be mapped to {TargetCls.__name__}'"
    )
