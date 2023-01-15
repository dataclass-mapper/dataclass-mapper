import sys
from dataclasses import dataclass, field
from typing import List, Optional

import pytest

from dataclass_mapper.classmeta import FieldMeta, get_class_meta
from dataclass_mapper.namespace import Namespace


def test_dataclass_normal_field() -> None:
    @dataclass
    class Foo:
        x: int
        y: str
        z: List[int]

    fields = get_class_meta(Foo, namespace=Namespace(locals={}, globals={})).fields
    assert fields == {
        "x": FieldMeta(name="x", type=int, allow_none=False, required=True),
        "y": FieldMeta(name="y", type=str, allow_none=False, required=True),
        "z": FieldMeta(name="z", type=List[int], allow_none=False, required=True),
    }


def test_dataclass_optional_fields() -> None:
    @dataclass
    class Foo:
        x: Optional[int]
        y: Optional[List[int]]

    fields = get_class_meta(Foo, namespace=Namespace(locals={}, globals={})).fields
    assert fields["x"].type is int
    assert fields["x"].allow_none
    assert not fields["x"].disallow_none
    assert str(fields["y"].type) == "typing.List[int]"
    assert fields["y"].allow_none


@pytest.mark.skipif(sys.version_info < (3, 10), reason="Union types are introduced for Python 3.10")
def test_dataclass_optional_fields_with_union():
    @dataclass
    class Foo:
        x: int | None

    fields = get_class_meta(Foo, namespace=Namespace(locals={}, globals={})).fields
    assert fields["x"].type is int
    assert fields["x"].allow_none
    assert not fields["x"].disallow_none


def test_dataclass_defaults_field() -> None:
    @dataclass
    class Foo:
        a: int
        b: Optional[str]
        c: int = 5
        d: Optional[str] = None
        e: Optional[str] = field(default="hello")
        f: Optional[str] = field(default_factory=lambda: "hello")

    fields = get_class_meta(Foo, namespace=Namespace(locals={}, globals={})).fields
    assert fields["a"].required
    assert fields["b"].required
    assert not fields["c"].required
    assert not fields["d"].required
    assert not fields["e"].required
    assert not fields["f"].required


@pytest.mark.skip("init=False is currently not supported")
def test_dataclass_non_init_field() -> None:
    @dataclass
    class Foo:
        a: int = field(init=False)

    fields = get_class_meta(Foo, namespace=Namespace(locals={}, globals={})).fields
    assert "a" not in fields
