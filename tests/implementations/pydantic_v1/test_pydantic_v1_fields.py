from __future__ import annotations

import sys
from typing import List, Optional

import pytest

from dataclass_mapper.classmeta import Namespace, get_class_meta
from dataclass_mapper.fieldtypes import ClassFieldType, ListFieldType, OptionalFieldType, compute_field_type
from dataclass_mapper.implementations.pydantic_v1 import PydanticV1FieldMeta, pydantic_version

if pydantic_version()[0] != 1:
    pytest.skip("V1 validators syntax", allow_module_level=True)

from pydantic import BaseModel, Field

empty_namespace = Namespace(locals={}, globals={})


def test_pydantic_normal_field() -> None:
    class Foo(BaseModel):
        x: int
        y: str
        z: List[int]

    fields = get_class_meta(Foo, namespace=empty_namespace).fields
    assert fields == {
        "x": PydanticV1FieldMeta(name="x", type=compute_field_type(int), required=True, alias="x"),
        "y": PydanticV1FieldMeta(name="y", type=compute_field_type(str), required=True, alias="y"),
        "z": PydanticV1FieldMeta(name="z", type=compute_field_type(List[int]), required=True, alias="z"),
    }


def test_pydantic_optional_fields() -> None:
    class Foo(BaseModel):
        x: Optional[int]
        y: Optional[List[int]]

    fields = get_class_meta(Foo, namespace=empty_namespace).fields
    assert fields["x"].type == OptionalFieldType(ClassFieldType(int))
    assert fields["y"].type == OptionalFieldType(ListFieldType(ClassFieldType(int)))


@pytest.mark.skipif(sys.version_info < (3, 10), reason="Union types are introduced for Python 3.10")
def test_pydantic_optional_fields_with_union():
    class Foo(BaseModel):
        x: int | None

    fields = get_class_meta(Foo, namespace=empty_namespace).fields
    assert fields["x"].type == OptionalFieldType(ClassFieldType(int))


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

    fields = get_class_meta(Foo, namespace=empty_namespace).fields
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

    fields = get_class_meta(Foo, namespace=empty_namespace).fields
    assert fields["a"].name == "a"
    assert fields["a"].alias == "b"

    assert fields["c"].name == "c"
    assert fields["c"].alias == "c"

    class Bar(BaseModel):
        a: int

        class Config:
            def alias_generator(x: str):  # type: ignore[misc]
                return x.upper()

    fields = get_class_meta(Bar, namespace=empty_namespace).fields
    assert fields["a"].name == "a"
    assert fields["a"].alias == "A"

    class Baz(BaseModel):
        a: int

        class Config:
            fields = {"a": "aaa"}

    fields = get_class_meta(Baz, namespace=empty_namespace).fields
    assert fields["a"].name == "a"
    assert fields["a"].alias == "aaa"
