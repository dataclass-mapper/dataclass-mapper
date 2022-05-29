from dataclasses import MISSING
from dataclasses import Field as DataclassField
from dataclasses import dataclass
from typing import Any, Union, cast, get_args, get_origin


def is_optional(type_: Any) -> bool:
    # requires Python 3.8
    return get_origin(type_) is Union and type(None) in get_args(type_)


@dataclass
class Field:
    name: str
    type: Any
    allow_none: bool
    has_default: bool

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
    def from_dataclass(cls, field: DataclassField) -> "Field":
        has_default = field.default is not MISSING or field.default_factory is not MISSING
        if is_optional(field.type):
            real_types = [t for t in get_args(field.type) if t is not type(None)]
            assert len(real_types) == 1
            return cls(
                name=field.name,
                type=real_types[0],
                allow_none=True,
                has_default=has_default,
            )
        else:
            return cls(
                name=field.name,
                type=field.type,
                allow_none=False,
                has_default=has_default,
            )

    @classmethod
    def from_pydantic(cls, field: Any) -> "Field":
        return cls(
            name=field.name,
            type=field.outer_type_,
            allow_none=field.allow_none,
            has_default=not field.required,
        )
