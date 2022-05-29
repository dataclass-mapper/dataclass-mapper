from typing import Optional

from pydantic import BaseModel, Field

from safe_mapper.field import Field as MetaField
from safe_mapper.safe_mapper import get_class_fields


def test_pydantic_normal_field() -> None:
    class Foo(BaseModel):
        x: int
        y: str
        z: list[int]

    fields = get_class_fields(Foo)
    assert fields == {
        "x": MetaField(name="x", type=int, allow_none=False, has_default=False),
        "y": MetaField(name="y", type=str, allow_none=False, has_default=False),
        "z": MetaField(name="z", type=list[int], allow_none=False, has_default=False),
    }


def test_pydantic_optional_fields() -> None:
    class Foo(BaseModel):
        x: Optional[int]
        y: Optional[list[int]]

    fields = get_class_fields(Foo)
    assert fields["x"].type is int
    assert fields["x"].allow_none
    assert not fields["x"].disallow_none
    assert str(fields["y"].type) == "list[int]"
    assert fields["y"].allow_none


def test_pydantic_defaults_field() -> None:
    class Foo(BaseModel):
        a: int
        b1: Optional[str]
        b2: Optional[int] = ...  # type: ignore
        b3: Optional[int] = Field(...)
        c: int = 5
        d: Optional[str] = None
        e: Optional[str] = Field("hello")
        f: Optional[str] = Field(default="hello")
        g: Optional[str] = Field(default_factory=lambda: "hello")

    fields = get_class_fields(Foo)
    assert not fields["a"].has_default
    assert fields["b1"].has_default  # pydantic fills optionals fields automatically with None
    assert not fields["b2"].has_default  # however not for elipsis defaults
    assert not fields["b3"].has_default
    assert fields["c"].has_default
    assert fields["d"].has_default
    assert fields["e"].has_default
    assert fields["f"].has_default
    assert fields["g"].has_default
