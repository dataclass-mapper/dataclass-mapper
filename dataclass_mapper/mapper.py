from dataclasses import fields
from importlib import import_module
from typing import Any, Callable, Optional, Type, TypeVar, cast

from .classmeta import get_dataclass_type
from .field import MetaField
from .mapping_method import (
    ClassMeta,
    DataclassType,
    MappingMethodSourceCode,
    Other,
    StringFieldMapping,
    get_map_to_func_name,
)


def get_class_fields(cls: Any) -> dict[str, MetaField]:
    dataclass_type = get_dataclass_type(cls)
    if dataclass_type == DataclassType.DATACLASSES:
        return {field.name: MetaField.from_dataclass(field) for field in fields(cls)}
    elif dataclass_type == DataclassType.PYDANTIC:
        return {field.name: MetaField.from_pydantic(field) for field in cls.__fields__.values()}
    assert False, "unreachable code"


def _make_mapper(
    mapping: StringFieldMapping,
    source_cls: Any,
    target_cls: Any,
) -> tuple[str, dict[str, Callable], dict[str, Any]]:
    source_cls_meta = ClassMeta.from_class(source_cls)
    target_cls_meta = ClassMeta.from_class(target_cls)
    actual_source_fields = get_class_fields(source_cls)
    actual_target_fields = get_class_fields(target_cls)
    source_code = MappingMethodSourceCode(source_cls=source_cls_meta, target_cls=target_cls_meta)

    for target_field_name in actual_target_fields.keys():
        target = actual_target_fields[target_field_name]
        # mapping exists
        if target_field_name in mapping:
            raw_source = mapping[target_field_name]
            if isinstance(raw_source, str):
                source_code.add_mapping(target=target, source=actual_source_fields[raw_source])
            elif isinstance(raw_source, Other):
                if raw_source == Other.USE_DEFAULT:
                    if actual_target_fields[target_field_name].required:
                        # leaving the target empty and using the default value/factory is not possible,
                        # as the target doesn't have a default value/factory
                        raise ValueError(
                            f"'{target_field_name}' of '{target_cls.__name__}' cannot be set to USE_DEFAULT, as it has no default"
                        )
                else:
                    raise NotImplemented
            else:
                source_code.add_mapping(target=target, source=raw_source)
        # there's a variable with the same name in the source
        elif target_field_name in actual_source_fields:
            source_code.add_mapping(target=target, source=actual_source_fields[target_field_name])
        # not possible to map
        else:
            raise ValueError(
                f"'{target_field_name}' of '{target_cls.__name__}' has no mapping in '{source_cls.__name__}'"
            )

    for target_field_name in mapping.keys() - actual_target_fields.keys():
        raise ValueError(
            f"'{target_field_name}' of mapping in '{source_cls.__name__}' doesn't exist in '{target_cls.__name__}'"
        )

    return str(source_code), source_code.methods, {target_cls_meta.alias_name: target_cls}


T = TypeVar("T")


def mapper(TargetCls: Any, mapping: Optional[StringFieldMapping] = None) -> Callable[[T], T]:
    """Class decorator that adds a private mapper method, that maps the current class to the ``TargetCls``.
    The mapper method can be called using the ``map_to`` function.

    :param TargetCls: The class (target class) that you want to map an object of the current (source) class to.
    :param mapping: An optional dictionary which which it's possible to describe how each field in the target class gets initialized.
        Fields that are not specified will be mapped automatically.

        - ``{"x": "y"}`` means, that the field ``x`` of the target object will have the value of the ``y`` fields in the target object.
        - ``{"x": USE_DEFAULT}`` means, that the field ``x`` will be initialized with the default value / factory of that field.
        - ``{"x": lambda: 42}`` means, that the field ``x`` will be initialized with the value 42.
        - ``{"x": lambda self: self.x + 1}`` means, that the field ``x`` will be initialized with the incremented value ``x`` of the source object.
    """

    def wrapped(SourceCls: T) -> T:
        add_mapper_function(SourceCls=SourceCls, TargetCls=TargetCls, mapping=mapping)
        return SourceCls

    return wrapped


def mapper_from(SourceCls: Any, mapping: Optional[StringFieldMapping] = None) -> Callable[[T], T]:
    """Class decorator that adds a private mapper method, that maps an object of ``SourceCls`` to the current class.
    The mapper method can be called using the ``map_to`` function.

    :param SourceCls: the class (source class) that you want to map an object from to the current (target) class.
    :param mapping: an optional dictionary which which it's possible to describe how each field in the target class gets initialized.
    """

    def wrapped(TargetCls: T) -> T:
        add_mapper_function(SourceCls=SourceCls, TargetCls=TargetCls, mapping=mapping)
        return TargetCls

    return wrapped


def add_mapper_function(
    SourceCls: Any, TargetCls: Any, mapping: Optional[StringFieldMapping]
) -> None:
    field_mapping = mapping or cast(StringFieldMapping, {})

    map_code, factories, context = _make_mapper(
        field_mapping,
        source_cls=SourceCls,
        target_cls=TargetCls,
    )
    module = import_module(SourceCls.__module__)

    d: dict = {}
    exec(map_code, module.__dict__ | context, d)
    setattr(SourceCls, get_map_to_func_name(TargetCls), d["convert"])
    for name, factory in factories.items():
        setattr(SourceCls, name, factory)


def map_to(obj, TargetCls: Type[T]) -> T:
    """Maps the given object to an object of type ``TargetCls``, if such a safe mapping was defined for the type of the given object.
    Raises an ``NotImplementedError`` if no such mapping is defined.

    :param obj: the source object that you want to map to an object of type ``TargetCls``
    :param TargetCls: The (target) class that you want to map to.
    :return: the mapped object
    """
    func_name = get_map_to_func_name(TargetCls)
    if hasattr(obj, func_name):
        return cast(T, getattr(obj, func_name)())

    raise NotImplementedError(
        f"Object of type '{type(obj)}' cannot be mapped to {TargetCls.__name__}'"
    )
