import sys
from dataclasses import dataclass
from typing import Dict

import pytest

from dataclass_mapper.implementations.pydantic_v1 import pydantic_version
from dataclass_mapper.mapper import map_to, mapper

if pydantic_version()[0] == 0:
    pytest.skip("Pydantic tests", allow_module_level=True)

from pydantic import BaseModel


class BarPydantic(BaseModel):
    x: int
    y: str


@dataclass
class BarDataclass:
    x: int
    y: str


class BazPydantic(BaseModel):
    bar: Dict[str, BarPydantic]


def test_dict_rec_pydantic_mapper():
    @mapper(BarPydantic)
    class Bar(BaseModel):
        x: int
        y: str

    @mapper(BazPydantic)
    class Baz(BaseModel):
        bar: Dict[str, Bar]

    baz_before = Baz(bar={"x": Bar(x=42, y="answer")})
    baz_after = BazPydantic(bar={"x": BarPydantic(x=42, y="answer")})
    assert repr(map_to(baz_before, BazPydantic)) == repr(baz_after)


@dataclass
class BazDataclass:
    bar: Dict[str, BarDataclass]


def test_dict_rec_dataclass_mapper():
    @mapper(BarDataclass)
    @dataclass
    class Bar:
        x: int
        y: str

    @mapper(BazDataclass)
    @dataclass
    class Baz:
        bar: Dict[str, Bar]

    baz_before = Baz(bar={"x": Bar(x=42, y="answer")})
    baz_after = BazDataclass(bar={"x": BarDataclass(x=42, y="answer")})
    assert map_to(baz_before, BazDataclass) == baz_after


@pytest.mark.skipif(sys.version_info < (3, 9), reason="Using builtin collection types are introduced in Python 3.9")
def test_builtin_dict_type():
    @dataclass
    class Foo:
        x: dict[str, int]  # type: ignore[misc]

    @mapper(Foo)
    @dataclass
    class Bar:
        x: dict[str, int]  # type: ignore[misc]
