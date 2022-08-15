from dataclasses import dataclass, field
from typing import Optional

import pytest

from dataclass_mapper.mapper import FieldMeta, get_class_fields


def test_dataclass_normal_field() -> None:
    @dataclass
    class Foo:
        x: int
        y: str
        z: list[int]

    fields = get_class_fields(Foo)
    assert fields == {
        "x": FieldMeta(name="x", type=int, allow_none=False, required=True),
        "y": FieldMeta(name="y", type=str, allow_none=False, required=True),
        "z": FieldMeta(name="z", type=list[int], allow_none=False, required=True),
    }


def test_dataclass_optional_fields() -> None:
    @dataclass
    class Foo:
        x: Optional[int]
        y: Optional[list[int]]

    fields = get_class_fields(Foo)
    assert fields["x"].type is int
    assert fields["x"].allow_none
    assert not fields["x"].disallow_none
    assert str(fields["y"].type) == "list[int]"
    assert fields["y"].allow_none


def test_dataclass_defaults_field() -> None:
    @dataclass
    class Foo:
        a: int
        b: Optional[str]
        c: int = 5
        d: Optional[str] = None
        e: Optional[str] = field(default="hello")
        f: Optional[str] = field(default_factory=lambda: "hello")

    fields = get_class_fields(Foo)
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

    fields = get_class_fields(Foo)
    assert "a" not in fields
