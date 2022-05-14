from dataclasses import Field as DataclassField
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Field:
    name: str
    type: Any

    @classmethod
    def from_dataclass(cls, field: DataclassField) -> "Field":
        return cls(name=field.name, type=field.type)

    @classmethod
    def from_pydantic(cls, field: Any) -> "Field":
        name = field.name
        type_ = field.type_
        if field.allow_none:
            type_ = Optional[type_]
        return cls(name=name, type=type_)
