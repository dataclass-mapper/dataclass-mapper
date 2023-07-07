from __future__ import annotations

import sys
from typing import List, Optional

import pytest
from pydantic import BaseModel, Field

from dataclass_mapper.classmeta import Namespace, get_class_meta
from dataclass_mapper.implementations.pydantic_v2 import PydanticV2FieldMeta, pydantic_version

if pydantic_version() < (2, 0, 0):
    pytest.skip("V2 validators syntax", allow_module_level=True)

from pydantic import ConfigDict

empty_namespace = Namespace(locals={}, globals={})


def test_pydantic_normal_field() -> None:
    class Foo(BaseModel):
        x: int
        y: str
        z: List[int]

    fields = get_class_meta(Foo, namespace=empty_namespace).fields
    assert fields == {
        "x": PydanticV2FieldMeta(name="x", type=int, allow_none=False, required=True, alias=None),
        "y": PydanticV2FieldMeta(name="y", type=str, allow_none=False, required=True, alias=None),
        "z": PydanticV2FieldMeta(name="z", type=List[int], allow_none=False, required=True, alias=None),
    }


def test_pydantic_optional_fields() -> None:
    class Foo(BaseModel):
        x: Optional[int]
        y: Optional[List[int]]

    fields = get_class_meta(Foo, namespace=empty_namespace).fields
    assert fields["x"].type is int
    assert fields["x"].allow_none
    assert not fields["x"].disallow_none
    assert str(fields["y"].type) == "typing.List[int]"
    assert fields["y"].allow_none


@pytest.mark.skipif(sys.version_info < (3, 10), reason="Union types are introduced for Python 3.10")
def test_pydantic_optional_fields_with_union():
    class Foo(BaseModel):
        x: int | None

    fields = get_class_meta(Foo, namespace=empty_namespace).fields
    assert fields["x"].type is int
    assert fields["x"].allow_none
    assert not fields["x"].disallow_none


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
    assert fields["b1"].required  # with pydantic v2 this is now required
    assert fields["b2"].required
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
    assert fields["c"].alias is None

    class Bar(BaseModel):
        a: int

        model_config = ConfigDict(alias_generator=lambda x: x.upper())

    fields = get_class_meta(Bar, namespace=empty_namespace).fields
    assert fields["a"].name == "a"
    assert fields["a"].alias == "A"
