from typing import Optional

from pydantic import BaseModel, Field

from dataclass_mapper.classmeta import FieldMeta, get_class_meta


def test_pydantic_normal_field() -> None:
    class Foo(BaseModel):
        x: int
        y: str
        z: list[int]

    fields = get_class_meta(Foo).fields
    assert fields == {
        "x": FieldMeta(name="x", type=int, allow_none=False, required=True, alias="x"),
        "y": FieldMeta(name="y", type=str, allow_none=False, required=True, alias="y"),
        "z": FieldMeta(name="z", type=list[int], allow_none=False, required=True, alias="z"),
    }


def test_pydantic_optional_fields() -> None:
    class Foo(BaseModel):
        x: Optional[int]
        y: Optional[list[int]]

    fields = get_class_meta(Foo).fields
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

    fields = get_class_meta(Foo).fields
    assert fields["a"].required
    assert not fields["b1"].required  # pydantic fills optionals fields automatically with None
    assert fields["b2"].required  # however not for elipsis defaults
    assert fields["b3"].required
    assert not fields["c"].required
    assert not fields["d"].required
    assert not fields["e"].required
    assert not fields["f"].required
    assert not fields["g"].required


def test_pydantic_alias() -> None:
    class Foo(BaseModel):
        a: int = Field(alias="b")
        c: int

    fields = get_class_meta(Foo).fields
    assert fields["a"].name == "a"
    assert fields["a"].alias == "b"

    assert fields["c"].name == "c"
    assert fields["c"].alias == "c"

    class Bar(BaseModel):
        a: int

        class Config:
            alias_generator = lambda x: x.upper()

    fields = get_class_meta(Bar).fields
    assert fields["a"].name == "a"
    assert fields["a"].alias == "A"

    class Baz(BaseModel):
        a: int

        class Config:
            fields = {"a": "aaa"}

    fields = get_class_meta(Baz).fields
    assert fields["a"].name == "a"
    assert fields["a"].alias == "aaa"
