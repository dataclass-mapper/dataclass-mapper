from copy import deepcopy
from importlib import import_module
from typing import Any, Callable, Dict, Optional, Tuple, Type, TypeVar, Union, cast, overload

from dataclass_mapper.fieldtypes.optional import OptionalFieldType

from .classmeta import get_class_meta
from .enum import EnumMapping, make_enum_mapper
from .mapping_method import (
    AssumeNotNone,
    CreateMappingMethodSourceCode,
    FromExtra,
    Ignore,
    MappingMethodSourceCode,
    StringSqlAlchemyFieldMapping,
    UpdateMappingMethodSourceCode,
)
from .mapping_preparation import (
    convert_sqlalchemy_fields,
    generate_missing_mappings,
    normalize_deprecated_mappings,
    raise_if_mapping_doesnt_match_target,
)
from .namespace import Namespace, get_namespace
from .utils import get_map_to_func_name, get_mapupdate_to_func_name


def _make_mapper(
    mapping: StringSqlAlchemyFieldMapping,
    source_cls: Any,
    target_cls: Any,
    namespace: Namespace,
    source_code_type: Type[MappingMethodSourceCode],
) -> Tuple[str, Dict[str, Callable], Dict[str, Any]]:
    source_cls_meta = get_class_meta(source_cls, namespace=namespace)
    target_cls_meta = get_class_meta(target_cls, namespace=namespace)
    actual_source_fields = source_cls_meta.fields
    actual_target_fields = target_cls_meta.fields

    string_field_mapping = convert_sqlalchemy_fields(
        mapping, source_cls_meta=source_cls_meta, target_cls_meta=target_cls_meta
    )
    string_field_mapping = generate_missing_mappings(
        string_field_mapping, actual_source_fields=actual_source_fields, actual_target_fields=actual_target_fields
    )
    raise_if_mapping_doesnt_match_target(
        string_field_mapping, source_cls=source_cls, target_cls=target_cls, actual_target_fields=actual_target_fields
    )
    normalized_mapping = normalize_deprecated_mappings(string_field_mapping)

    source_code = source_code_type(source_cls=source_cls_meta, target_cls=target_cls_meta)
    for target_field_name, raw_source in normalized_mapping.items():
        target_field = actual_target_fields[target_field_name]
        if isinstance(raw_source, str):
            source_field_name = raw_source
            if source_field_name not in actual_source_fields:
                raise ValueError(
                    f"'{source_field_name}' of mapping in '{source_cls.__name__}' doesn't exist "
                    f"in '{source_cls.__name__}'"
                )
            source_code.add_mapping(target=target_field, source=actual_source_fields[source_field_name])
        elif isinstance(raw_source, AssumeNotNone):
            source_field_name = raw_source.field_name or target_field.name
            if source_field_name not in actual_source_fields:
                raise ValueError(
                    f"'{source_field_name}' of mapping in '{source_cls.__name__}' doesn't exist "
                    f"in '{source_cls.__name__}'"
                )
            source_field = deepcopy(actual_source_fields[source_field_name])
            # pretend like the source field isn't optional
            if isinstance(source_field.type, OptionalFieldType):
                source_field.type = source_field.type.inner_type
            source_code.add_mapping(target=target_field, source=source_field)
        elif isinstance(raw_source, FromExtra):
            source_code.add_from_extra(target=target_field, source=raw_source)
        elif isinstance(raw_source, Ignore):
            if source_code_type.all_required_fields_need_initialization and target_field.required:
                # leaving the target empty and using the default value/factory is not possible,
                # as the target doesn't have a default value/factory
                raise ValueError(
                    f"'{target_field_name}' of '{target_cls.__name__}' cannot be set to {raw_source.created_via}, "
                    "as it has no default"
                )
        elif callable(raw_source):
            source_code.add_callable(target=target_field, source=raw_source)
        else:
            assert False, "impossible to reach"

    return str(source_code), source_code.methods, {target_cls_meta.alias_name: target_cls}


def create_mapper(
    SourceCls: Any, TargetCls: Any, mapping: Optional[StringSqlAlchemyFieldMapping] = None, only_update: bool = False
) -> None:
    """Creates a private mapper method, that maps the ``SourceCls`` to the ``TargetCls``.
    The mapper method can be called using the :func:`map_to` function.

    :param SourceCls: the class (source class) that you want to map an object from to the current (target) class.
    :param TargetCls: The class (target class) that you want to map an object of the current (source) class to.
    :param mapping: An optional dictionary which which it's possible to describe how each field in the target
        class gets initialized.
        Fields that are not specified will be mapped automatically.
        Every single field in the target class must have some mapping (in order to not forget about a field),
        either a default mapping (if the field names match), or an explicit mapping definition with this
        `mapping` parameter.

        - ``{"x": "y"}`` means, that the field ``x`` of the target object will be initialized with the value of the
          ``y`` fields in the source object.
        - ``{"x": lambda: 42}`` means, that the field ``x`` will be initialized with the value 42.
        - ``{"x": lambda self: self.x + 1}`` means, that the field ``x`` will be initialized with the
          incremented value ``x`` of the source object.
        - ``{"x": USE_DEFAULT}`` (deprecated) means, nothing is mapped to the field ``x``, it will just be
          initialized with the default value / factory of that field, or simply ignored during an update.
        - ``{"x": IGNORE_MISSING_MAPPING}`` (deprecated) means, nothing is mapped to the field ``x``, it will just be
          initialized with the default value / factory of that field, or simply ignored during an update.
        - ``{"x": init_with_default()}`` means, nothing is mapped to the field ``x``, it will just be
          initialized with the default value / factory of that field, or simply ignored during an update.
        - ``{"x": ignore()}`` means, nothing is mapped to the field ``x``, it will just be
          initialized with the default value / factory of that field, or simply ignored during an update.
        - ``{"x": assume_not_none("y")}`` means, that the target field ``x`` will be initialized with the value of the
          ``y`` source field, and the library will assume that the source field is not ``None``.
          If no source field name is given, it will additionally assume that the source field is also called ``x``.
        - ``{"x": provide_with_extra()}`` means, that you don't fill this field with any field of the source class,
          but with the extra dictionary given by the :func:`map_to` method.
    :param only_update: Per default the mapping is used both for creating a new object, and for updating an existing
        object. With ``only_update`` you can use it only for updates, which allows ignoring fields that would be
        necessary during the creation of a new object.
    """

    namespace = get_namespace()
    add_mapper_function(
        SourceCls=SourceCls, TargetCls=TargetCls, mapping=mapping, namespace=namespace, only_update=only_update
    )


T = TypeVar("T")


def mapper(
    TargetCls: Any, mapping: Optional[StringSqlAlchemyFieldMapping] = None, only_update: bool = False
) -> Callable[[T], T]:
    """Class decorator that adds a private mapper method, that maps the current class to the ``TargetCls``.
    The mapper method can be called using the :func:`map_to` function.

    :param TargetCls: The class (target class) that you want to map an object of the current (source) class to.
    :param mapping: an optional dictionary which which it's possible to describe how each field in the target class
        gets initialized (see  :func:`create_mapper`)
    :param only_update: Per default the mapping is used both for creating a new object, and for updating an existing
        object. With ``only_update`` you can use it only for updates, which allows ignoring fields that would be
        necessary during the creation of a new object.
    """

    namespace = get_namespace()

    def wrapped(SourceCls: T) -> T:
        add_mapper_function(
            SourceCls=SourceCls, TargetCls=TargetCls, mapping=mapping, namespace=namespace, only_update=only_update
        )
        return SourceCls

    return wrapped


def mapper_from(
    SourceCls: Any, mapping: Optional[StringSqlAlchemyFieldMapping] = None, only_update: bool = False
) -> Callable[[T], T]:
    """Class decorator that adds a private mapper method, that maps an object of ``SourceCls`` to the current class.
    The mapper method can be called using the :func:`map_to` function.

    :param SourceCls: the class (source class) that you want to map an object from to the current (target) class.
    :param mapping: an optional dictionary which which it's possible to describe how each field in the target class
        gets initialized (see  :func:`create_mapper`)
    :param only_update: Per default the mapping is used both for creating a new object, and for updating an existing
        object. With ``only_update`` you can use it only for updates, which allows ignoring fields that would be
        necessary during the creation of a new object.
    """

    namespace = get_namespace()

    def wrapped(TargetCls: T) -> T:
        add_mapper_function(
            SourceCls=SourceCls, TargetCls=TargetCls, mapping=mapping, namespace=namespace, only_update=only_update
        )
        return TargetCls

    return wrapped


def add_mapper_function(
    SourceCls: Any,
    TargetCls: Any,
    mapping: Optional[StringSqlAlchemyFieldMapping],
    namespace: Namespace,
    only_update: bool,
) -> None:
    field_mapping = mapping or cast(StringSqlAlchemyFieldMapping, {})

    if not only_update:
        create_map_func_name = get_map_to_func_name(TargetCls)
        add_specific_mapper_function(
            SourceCls=SourceCls,
            TargetCls=TargetCls,
            field_mapping=field_mapping,
            source_code_type=CreateMappingMethodSourceCode,
            namespace=namespace,
            map_func_name=create_map_func_name,
        )

    update_map_func_name = get_mapupdate_to_func_name(TargetCls)
    add_specific_mapper_function(
        SourceCls=SourceCls,
        TargetCls=TargetCls,
        field_mapping=field_mapping,
        source_code_type=UpdateMappingMethodSourceCode,
        namespace=namespace,
        map_func_name=update_map_func_name,
    )


def add_specific_mapper_function(
    SourceCls: Any,
    TargetCls: Any,
    field_mapping: StringSqlAlchemyFieldMapping,
    namespace: Namespace,
    source_code_type: Type[MappingMethodSourceCode],
    map_func_name: str,
) -> None:
    map_code, factories, context = _make_mapper(
        field_mapping,
        source_cls=SourceCls,
        target_cls=TargetCls,
        namespace=namespace,
        source_code_type=source_code_type,
    )

    module = import_module(SourceCls.__module__)

    d: Dict = {}
    # Support older versions of python by calling {**a, **b} rather than a|b
    exec(map_code, {**module.__dict__, **context}, d)

    if hasattr(SourceCls, map_func_name):
        raise AttributeError(
            f"There already exists a mapping between '{SourceCls.__name__}' and '{TargetCls.__name__}'"
        )
    setattr(SourceCls, map_func_name, d[source_code_type.func_name])
    for name, factory in factories.items():
        setattr(SourceCls, name, factory)


def create_enum_mapper(SourceCls: Any, TargetCls: Any, mapping: Optional[EnumMapping] = None) -> None:
    """Creates a private mapper method, that maps the enum class ``SourceCls`` to the
    enum class ``TargetCls``. The mapper method can be called using the :func:`map_to` function.

    :param SourceCls: The enum class (source class) that you want to map an object of the current
        (source) enum class to.
    :param TargetCls: The enum class (source class) that you want to map members from to the current
        (target) enum class to.
    :param mapping: An optional dictionary which which it's possible to describe to which member of the
        target class a member of the source class is mapped to.
        Key/value of the mapping can either be the names of the enum members, or the members themselves.
        Fields that are not specified will be mapped automatically.
        Every single field in the source class must have some mapping,
        either a default mapping (if the member names match), or an explicit mapping definition with
        this `mapping` parameter.

        - ``{"x": "y"}`` means, that the member ``x`` of the source enum will get mapped to the
          member ``y`` in the target object.
    """

    add_enum_mapper_function(SourceCls=SourceCls, TargetCls=TargetCls, mapping=mapping)


def enum_mapper(TargetCls: Any, mapping: Optional[EnumMapping] = None) -> Callable[[T], T]:
    """Class decorator that adds a private mapper method, that maps the current enum class to the
    enum class ``TargetCls``. The mapper method can be called using the :func:`map_to` function.

    :param TargetCls: The enum class (source class) that you want to map members from to the current
        (target) enum class to.
    :param mapping: An optional dictionary which which it's possible to describe to which member of the
        target class a member of the source class is mapped to (see :func:`create_enum_mapper`).
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
    """Class decorator that adds a private mapper method, that maps members of the enum class ``SourceCls`` to
    members of the current enum class.
    The mapper method can be called using the :func:`map_to` function.

    :param SourceCls: The enum class (source class) that you want to map an object of the current
        (source) enum class to.
    :param mapping: An optional dictionary which which it's possible to describe to which member of the
        target class a member of the source class is mapped to (see :func:`create_enum_mapper`).
    """

    def wrapped(TargetCls: T) -> T:
        add_enum_mapper_function(
            SourceCls=SourceCls,
            TargetCls=TargetCls,
            mapping=mapping,
        )
        return TargetCls

    return wrapped


def add_enum_mapper_function(SourceCls: Any, TargetCls: Any, mapping: Optional[EnumMapping]) -> None:
    convert_function = make_enum_mapper(
        source_cls=SourceCls,
        target_cls=TargetCls,
        mapping=mapping or cast(EnumMapping, {}),
    )
    map_func_name = get_map_to_func_name(TargetCls)
    if hasattr(SourceCls, map_func_name):
        raise AttributeError(
            f"There already exists a mapping between '{SourceCls.__name__}' and '{TargetCls.__name__}'"
        )
    setattr(SourceCls, map_func_name, convert_function)


@overload
def map_to(obj, target: Type[T], extra: Optional[Dict[str, Any]] = None) -> T:
    pass


@overload
def map_to(obj, target: T, extra: Optional[Dict[str, Any]] = None) -> T:
    pass


def map_to(obj, target: Union[Type[T], T], extra: Optional[Dict[str, Any]] = None) -> T:
    """Given a target class, it will create a new object of that type using the defined mapping.
    Given a target object, it will update that object using the defined mapping.

    If no suitable mapping was defined for the type, it will raise an ``NotImplementedError``.

    :param obj: the source object that you want to map to an object of type ``TargetCls``
    :param target: the target or the target class that you want to map to.
    :param extra: dictionary with the values for the `provide_with_extra()` fields
    :return: the mapped object
    """
    if extra is None:
        extra = {}

    if isinstance(target, type):
        TargetCls = target
        func_name = get_map_to_func_name(target)

        if hasattr(obj, func_name):
            return cast(T, getattr(obj, func_name)(extra))
    else:
        TargetCls = target.__class__
        func_name = get_mapupdate_to_func_name(TargetCls)

        if hasattr(obj, func_name):
            return cast(T, getattr(obj, func_name)(target, extra))

    raise NotImplementedError(f"Object of type '{type(obj).__name__}' cannot be mapped to '{TargetCls.__name__}'")
