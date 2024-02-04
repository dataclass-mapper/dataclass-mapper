from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Dict, Optional, Union

from dataclass_mapper.implementations.sqlalchemy import InstrumentedAttribute


class Spezial(Enum):
    USE_DEFAULT = auto()
    IGNORE_MISSING_MAPPING = auto()


@dataclass(frozen=True)
class Ignore:
    created_via: str


def init_with_default() -> Ignore:
    """Initialize the target field with the default value, or default factory."""
    return Ignore(created_via="init_with_default()")


def ignore() -> Ignore:
    """If the mapping operation creates a new object, it will initialize the target field
    with the default value, or default factory.
    If the mapping operation updates a field, it will simply ignore that field and keep the
    old value.
    """
    return Ignore(created_via="ignore()")


@dataclass(frozen=True)
class AssumeNotNone:
    field_name: Optional[str] = None


def assume_not_none(field_name: Optional[str] = None) -> AssumeNotNone:
    """Assume that the source field is not none, even if it is an optional field.
    Allows a mapping from ``Optional[T]`` to ``T``.
    If the field name is not specified, it is assumed that the source field has the same name as the target field.
    """
    return AssumeNotNone(field_name)


@dataclass(frozen=True)
class FromExtra:
    name: str


def from_extra(name: str) -> FromExtra:
    """Don't map this field using a source class field, fill it with a dictionary called `extra` duing `map_to`."""
    return FromExtra(name)


@dataclass(frozen=True)
class UpdateOnlyIfSet:
    field_name: Optional[str] = None


def update_only_if_set(field_name: Optional[str] = None) -> UpdateOnlyIfSet:
    """Only update the target field, if the source field is not ``None``.
    Therefore this allows a mapping from ``Optional[T]`` to ``T``.
    If the field name is not specified, it is assumed that the source field has the same name as the target field.
    """
    return UpdateOnlyIfSet(field_name)


CallableWithMax1Parameter = Union[Callable[[], Any], Callable[[Any], Any]]


# the different types that can be used as origin (source) for mapping to a member
# - str: the name of a different variable in the original class
# - Callable: a function that produces the value (can use `self` as parameter)
# - Other.USE_DEFAULT/IGNORE_MISSING_MAPPING/init_with_default()/ignore(): Don't map to this variable
#   (only allowed if there is a default value/factory for it)
# - assume_not_none(): assume that the source field is not None
# - from_extra(): create no mapping between the classes, fill the field with a dictionary called `extra`
CurrentOrigin = Union[str, CallableWithMax1Parameter, Ignore, AssumeNotNone, FromExtra, UpdateOnlyIfSet]
Origin = Union[CurrentOrigin, Spezial]
CurrentStringFieldMapping = Dict[str, CurrentOrigin]
StringFieldMapping = Dict[str, Origin]
StringSqlAlchemyFieldMapping = Dict[Union[str, InstrumentedAttribute], Union[Origin, InstrumentedAttribute]]
