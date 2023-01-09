import warnings
from copy import deepcopy
from importlib import import_module
from itertools import zip_longest
from typing import Any, Callable, Optional, Type, TypeVar, cast

from .assignments import get_map_to_func_name
from .classmeta import get_class_meta
from .enum import EnumMapping, make_enum_mapper
from .mapping_method import (
    AssumeNotNone,
    InitWithDefault,
    MappingMethodSourceCode,
    ProvideWithExtra,
    Spezial,
    StringFieldMapping,
)


def _make_mapper(
    mapping: StringFieldMapping,
    source_cls: Any,
    target_cls: Any,
) -> tuple[str, dict[str, Callable], dict[str, Any]]:
    source_cls_meta = get_class_meta(source_cls)
    target_cls_meta = get_class_meta(target_cls)
    actual_source_fields = source_cls_meta.fields
    actual_target_fields = target_cls_meta.fields
    source_code = MappingMethodSourceCode(source_cls=source_cls_meta, target_cls=target_cls_meta)

    for target_field_name, target_field in actual_target_fields.items():
        # mapping exists
        if target_field_name in mapping:
            raw_source = mapping[target_field_name]
            if isinstance(raw_source, str):
                source_field_name = raw_source
                if source_field_name not in actual_source_fields:
                    raise ValueError(
                        f"'{source_field_name}' of mapping in '{source_cls.__name__}' doesn't exist in '{source_cls.__name__}'"
                    )
                source_code.add_mapping(
                    target=target_field, source=actual_source_fields[source_field_name]
                )
            elif isinstance(raw_source, AssumeNotNone):
                source_field_name = raw_source.field_name or target_field.name
                if source_field_name not in actual_source_fields:
                    raise ValueError(
                        f"'{source_field_name}' of mapping in '{source_cls.__name__}' doesn't exist in '{source_cls.__name__}'"
                    )
                source_field = deepcopy(actual_source_fields[source_field_name])
                # pretend like the source field isn't optional
                source_field.allow_none = False
                source_code.add_mapping(target=target_field, source=source_field)
            elif isinstance(raw_source, ProvideWithExtra):
                source_code.add_fill_with_extra(target=target_field)
            elif isinstance(raw_source, (Spezial, InitWithDefault)):
                if raw_source in (
                    Spezial.USE_DEFAULT,
                    Spezial.IGNORE_MISSING_MAPPING,
                ) or isinstance(raw_source, InitWithDefault):
                    if raw_source is Spezial.USE_DEFAULT:
                        warnings.warn(
                            "USE_DEFAULT is deprecated, use init_with_default() instead",
                            DeprecationWarning,
                        )
                    if raw_source is Spezial.IGNORE_MISSING_MAPPING:
                        warnings.warn(
                            "IGNORE_MISSING_MAPPING is deprecated, use init_with_default() instead",
                            DeprecationWarning,
                        )

                    if target_field.required:
                        # leaving the target empty and using the default value/factory is not possible,
                        # as the target doesn't have a default value/factory
                        setting_name = (
                            raw_source.name
                            if isinstance(raw_source, Spezial)
                            else "init_with_default()"
                        )
                        raise ValueError(
                            f"'{target_field_name}' of '{target_cls.__name__}' cannot be set to {setting_name}, as it has no default"
                        )
                else:
                    raise NotImplemented
            else:
                source_code.add_mapping(target=target_field, source=raw_source)
        # there's a variable with the same name in the source
        elif target_field_name in actual_source_fields:
            source_code.add_mapping(
                target=target_field, source=actual_source_fields[target_field_name]
            )
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
        Every single field in the target class must have some mapping (in order to not forget about a field),
        either a default mapping (if the field names match), or an explicit mapping definition with this `mapping` parameter.

        - ``{"x": "y"}`` means, that the field ``x`` of the target object will have the value of the ``y`` fields in the target object.
        - ``{"x": lambda: 42}`` means, that the field ``x`` will be initialized with the value 42.
        - ``{"x": lambda self: self.x + 1}`` means, that the field ``x`` will be initialized with the incremented value ``x`` of the source object.
        - ``{"x": USE_DEFAULT}`` (deprecated) means, nothing is mapped to the field ``x``, it will just be initialized with the default value / factory of that field.
        - ``{"x": IGNORE_MISSING_MAPPING}`` (deprecated) means, nothing is mapped to the field ``x``, it will just be initialized with the default value / factory of that field.
        - ``{"x": init_with_default()}`` means, nothing is mapped to the field ``x``, it will just be initialized with the default value / factory of that field.
        - ``{"x": assume_not_none("y")}`` means, that the target field ``x`` will have the value of the ``y`` source field, and the library will assume that the source field might be optional. If no source field name is given, it will additionally assume that the source field is also called ``x``.
        - ``{"x": provide_with_extra()}`` means, that you don't fill this field with any field of the source class, but with the extra dictionary given by the `map_to` method.
    """

    def wrapped(SourceCls: T) -> T:
        add_mapper_function(
            SourceCls=SourceCls,
            TargetCls=TargetCls,
            mapping=mapping,
        )
        return SourceCls

    return wrapped


def mapper_from(SourceCls: Any, mapping: Optional[StringFieldMapping] = None) -> Callable[[T], T]:
    """Class decorator that adds a private mapper method, that maps an object of ``SourceCls`` to the current class.
    The mapper method can be called using the ``map_to`` function.

    :param SourceCls: the class (source class) that you want to map an object from to the current (target) class.
    :param mapping: an optional dictionary which which it's possible to describe how each field in the target class gets initialized.
    """

    def wrapped(TargetCls: T) -> T:
        add_mapper_function(
            SourceCls=SourceCls,
            TargetCls=TargetCls,
            mapping=mapping,
        )
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
    setattr(SourceCls, "__zip_longest", zip_longest)
    exec(map_code, module.__dict__ | context, d)
    setattr(SourceCls, get_map_to_func_name(TargetCls), d["convert"])
    for name, factory in factories.items():
        setattr(SourceCls, name, factory)


def enum_mapper(TargetCls: Any, mapping: Optional[EnumMapping] = None) -> Callable[[T], T]:
    """Class decorator that adds a private mapper method, that maps the current enum class to the enum class ``TargetCls``.
    The mapper method can be called using the ``map_to`` function.

    :param TargetCls: The enum class (source class) that you want to map members from to the current (target) enum class to.
    :param mapping: An optional dictionary which which it's possible to describe to which member of the target class a member of the source class is mapped to.
        Key/value of the mapping can either be the names of the enum members, or the members themselves.
        Fields that are not specified will be mapped automatically.
        Every single field in the source class must have some mapping,
        either a default mapping (if the member names match), or an explicit mapping definition with this `mapping` parameter.

        - ``{"x": "y"}`` means, that the member ``x`` of the source enum will get mapped to the member ``y`` in the target object.
    """

    def wrapped(SourceCls: T) -> T:
        add_enum_mapper_function(
            SourceCls=SourceCls,
            TargetCls=TargetCls,
            mapping=mapping,
        )
        return SourceCls

    return wrapped


def enum_mapper_from(SourceCls: Any, mapping: Optional[EnumMapping] = None) -> Callable[[T], T]:
    """Class decorator that adds a private mapper method, that maps members of the enum class ``SourceCls`` to members of the current enum class.
    The mapper method can be called using the ``map_to`` function.

    :param SourceCls: The enum class (source class) that you want to map an object of the current (source) enum class to.
    :param mapping: An optional dictionary which which it's possible to describe to which member of the target class a member of the source class is mapped to.
    """

    def wrapped(TargetCls: T) -> T:
        add_enum_mapper_function(
            SourceCls=SourceCls,
            TargetCls=TargetCls,
            mapping=mapping,
        )
        return TargetCls

    return wrapped


def add_enum_mapper_function(
    SourceCls: Any, TargetCls: Any, mapping: Optional[EnumMapping]
) -> None:
    convert_function = make_enum_mapper(
        source_cls=SourceCls,
        target_cls=TargetCls,
        mapping=mapping or cast(EnumMapping, {}),
    )
    setattr(SourceCls, get_map_to_func_name(TargetCls), convert_function)


def map_to(obj, TargetCls: Type[T], extra: Optional[dict[str, Any]] = None) -> T:
    """Maps the given object to an object of type ``TargetCls``, if such a safe mapping was defined for the type of the given object.
    Raises an ``NotImplementedError`` if no such mapping is defined.

    :param obj: the source object that you want to map to an object of type ``TargetCls``
    :param TargetCls: the (target) class that you want to map to.
    :param extra: dictionary with the values for the `provide_with_extra()` fields
    :return: the mapped object
    """
    if extra is None:
        extra = {}
    func_name = get_map_to_func_name(TargetCls)
    if hasattr(obj, func_name):
        return cast(T, getattr(obj, func_name)(extra))

    raise NotImplementedError(
        f"Object of type '{type(obj).__name__}' cannot be mapped to '{TargetCls.__name__}'"
    )
