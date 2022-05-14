from dataclasses import fields, is_dataclass
from importlib import import_module
from typing import Any, Callable, Optional, Type, TypeVar, cast

from .field import Field
from .mapping_method import MappingMethodSourceCode, get_map_to_func_name


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


def _make_mapper(mapping: dict[str, str], source_cls: Any, target_cls: Any) -> str:
    actual_source_fields = get_class_fields(source_cls)
    actual_target_fields = get_class_fields(target_cls)
    source_code = MappingMethodSourceCode(
        source_cls=source_cls,
        target_cls=target_cls,
        actual_source_fields=actual_source_fields,
        actual_target_fields=actual_target_fields,
    )
    mapped_target_fields = set(mapping)

    for target_field, source_field in mapping.items():
        if target_field in actual_target_fields:
            source_code.add_mapping(target_field, source_field)
        else:
            raise ValueError(
                f"'{target_field}' of mapping in '{source_cls.__name__}' doesn't exist in '{target_cls.__name__}'"
            )

    # handle missing fields
    for field in actual_target_fields.keys() - mapped_target_fields:
        if field in actual_source_fields:
            source_code.add_mapping(field, field)
        else:
            raise ValueError(
                f"'{field}' of '{target_cls.__name__}' has no mapping in '{source_cls.__name__}'"
            )

    return str(source_code)


T = TypeVar("T")


def safe_mapper(TargetCls: Any, mapping: Optional[dict[str, str]] = None) -> Callable[[T], T]:
    """Adds a private mapper method to the class, that maps the current class to the `TargetCls`.
    The mapper method can be called using the `map_to` function.

    With the `mapping` parameter you can additionally define attribute name changes, in the format `dict[TargetName, SourceName]`.
    """
    field_mapping = mapping or cast(dict[str, str], {})

    def wrapped(source_cls: T) -> T:
        map_code = _make_mapper(field_mapping, source_cls=source_cls, target_cls=TargetCls)
        module = import_module(TargetCls.__module__)

        d: dict = {}
        exec(map_code, module.__dict__, d)
        setattr(source_cls, get_map_to_func_name(TargetCls), d["convert"])

        return source_cls

    return wrapped


def map_to(obj, TargetCls: Type[T]) -> T:
    """Maps the given object to an object of type `TargetCls`, if such a safe mapping was defined for the type of the given object."""
    func_name = get_map_to_func_name(TargetCls)
    if not hasattr(obj, func_name):
        raise NotImplementedError(
            f"Object of type '{type(obj)}' cannot be mapped to {TargetCls.__name__}'"
        )
    return cast(T, getattr(obj, func_name)())
