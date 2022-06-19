from dataclasses import MISSING
from dataclasses import Field as DataclassField
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any, Union, cast, get_args, get_origin
from uuid import UUID


def is_optional(type_: Any) -> bool:
    # requires Python 3.8
    return get_origin(type_) is Union and type(None) in get_args(type_)


@dataclass
class MetaField:
    """Dataclass containing meta information about fields in dataclasses or pydantic classes.
    Information like the name and type of the field, and if it is required to set it.

    The type will contain the exact type of the field.
    However for optional fields, the Optional quantifier is removed, and `allow_none` is set accordingly.
    - int           => type = int, allow_none = False
    - Optional[int] => type = int, allow_none = True
    """

    name: str
    type: Any
    allow_none: bool
    required: bool

    @property
    def disallow_none(self) -> bool:
        return not self.allow_none

    @property
    def type_string(self) -> str:
        type_name = cast(str, self.type.__name__)
        if self.allow_none:
            type_name = f"Optional[{type_name}]"
        return type_name

    def __repr__(self) -> str:
        return f"'{self.name}' of type '{self.type_string}'"

    @classmethod
    def from_dataclass(cls, field: DataclassField) -> "MetaField":
        has_default = field.default is not MISSING or field.default_factory is not MISSING
        if is_optional(field.type):
            real_types = [t for t in get_args(field.type) if t is not type(None)]
            assert len(real_types) == 1
            return cls(
                name=field.name,
                type=real_types[0],
                allow_none=True,
                required=not has_default,
            )
        else:
            return cls(
                name=field.name,
                type=field.type,
                allow_none=False,
                required=not has_default,
            )

    @classmethod
    def from_pydantic(cls, field: Any) -> "MetaField":
        return cls(
            name=field.name,
            type=field.outer_type_,
            allow_none=field.allow_none,
            required=field.required,
        )

    @classmethod
    def from_sqlalchemy(cls, column: Any) -> "MetaField":
        if column.nullable:
            required = True
        else:
            required = column.default is None and column.server_default is None

        return cls(
            name=column.name,
            type=cls._extract_sqlalchemy_type(column.type),
            allow_none=column.nullable,
            required=required,
        )

    @classmethod
    def _extract_sqlalchemy_type(cls, type_):
        sqlalchemy = __import__("sqlalchemy")

        if isinstance(type_, sqlalchemy.dialects.postgresql.ARRAY):
            item_type = cls._extract_sqlalchemy_type(type_.item_type)
            return list[item_type]

        if isinstance(type_, sqlalchemy.Enum):
            return type_.enum_class

        type_mapping = {
            sqlalchemy.BigInteger: int,
            sqlalchemy.Boolean: bool,
            sqlalchemy.Date: date,
            sqlalchemy.DateTime: datetime,
            # sqlalchemy.Enum: ,
            sqlalchemy.Float: float,
            sqlalchemy.Integer: int,
            sqlalchemy.Interval: timedelta,
            sqlalchemy.LargeBinary: bytes,
            sqlalchemy.SmallInteger: int,
            sqlalchemy.String: str,
            sqlalchemy.Text: str,
            sqlalchemy.Time: time,
            sqlalchemy.Unicode: str,
            sqlalchemy.UnicodeText: str,
            sqlalchemy.dialects.postgresql.UUID: UUID,
        }

        for sqlalchemy_cls, mapped_type in type_mapping.items():
            if isinstance(type_, sqlalchemy_cls):
                return mapped_type

        return type_  # default, might be another table
