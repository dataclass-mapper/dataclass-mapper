from dataclasses import fields, is_dataclass
from importlib import import_module
from typing import Any, Callable, Optional, Type, TypeVar, cast
from uuid import uuid4

from .field import Field
from .mapping_method import MappingMethodSourceCode, Origin, get_map_to_func_name


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
) -> tuple[str, dict[str, Callable], dict[str, Any]]:
    actual_source_fields = get_class_fields(source_cls)
    actual_target_fields = get_class_fields(target_cls)
    target_cls_alias = f"_{uuid4().hex}"
    source_code = MappingMethodSourceCode(
        source_cls=source_cls,
        target_cls=target_cls,
        actual_source_fields=actual_source_fields,
        actual_target_fields=actual_target_fields,
        target_cls_alias=target_cls_alias,
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

    return str(source_code), source_code.methods, {target_cls_alias: target_cls}


T = TypeVar("T")


def safe_mapper(TargetCls: Any, mapping: Optional[dict[str, Origin]] = None) -> Callable[[T], T]:
    """Adds a private mapper method to the class, that maps the current class to the `TargetCls`.
    The mapper method can be called using the `map_to` function.

    With the `mapping` parameter you can additionally define attribute name changes, in the format `dict[TargetName, SourceName]`.
    """

    def wrapped(SourceCls: T) -> T:
        add_mapper_function(SourceCls=SourceCls, TargetCls=TargetCls, mapping=mapping)
        return SourceCls

    return wrapped


def safe_mapper_from(
    SourceCls: Any, mapping: Optional[dict[str, Origin]] = None
) -> Callable[[T], T]:
    """Adds a private mapper method to the class, that maps an object of `SourceCls` to the current class.
    The mapper method can be called using the `map_to` function.

    With the `mapping` parameter you can additionally define attribute name changes, in the format `dict[TargetName, SourceName]`.
    """

    def wrapped(TargetCls: T) -> T:
        add_mapper_function(SourceCls=SourceCls, TargetCls=TargetCls, mapping=mapping)
        return TargetCls

    return wrapped


def add_mapper_function(
    SourceCls: Any, TargetCls: Any, mapping: Optional[dict[str, Origin]]
) -> None:
    field_mapping = mapping or cast(dict[str, Origin], {})

    map_code, factories, context = _make_mapper(
        field_mapping,
        source_cls=SourceCls,
        target_cls=TargetCls,
    )
    module = import_module(SourceCls.__module__)

    d: dict = {}
    # print(f"mapper from {SourceCls} to {target_cls}")
    # print(map_code)
    # print()
    exec(map_code, module.__dict__ | context, d)
    setattr(SourceCls, get_map_to_func_name(TargetCls), d["convert"])
    for name, factory in factories.items():
        setattr(SourceCls, name, factory)


def map_to(obj, TargetCls: Type[T]) -> T:
    """Maps the given object to an object of type `TargetCls`, if such a safe mapping was defined for the type of the given object."""
    func_name = get_map_to_func_name(TargetCls)
    if hasattr(obj, func_name):
        return cast(T, getattr(obj, func_name)())

    raise NotImplementedError(
        f"Object of type '{type(obj)}' cannot be mapped to {TargetCls.__name__}'"
    )
