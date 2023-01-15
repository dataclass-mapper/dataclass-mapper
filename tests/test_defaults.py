from dataclasses import dataclass, field
from typing import List, Optional

import pytest
from pydantic import BaseModel, Field

from dataclass_mapper import IGNORE_MISSING_MAPPING, USE_DEFAULT, init_with_default, map_to, mapper


class BarPydantic(BaseModel):
    x: int = Field(default=5)
    y: str = "some_default"
    z: int = Field(default_factory=lambda: 1)


def test_pydantic_defaults_with_USE_DEFAULT():
    with pytest.deprecated_call():

        @mapper(
            BarPydantic,
            {"x": USE_DEFAULT, "y": USE_DEFAULT, "z": USE_DEFAULT},
        )
        class Bar(BaseModel):
            pass

        assert repr(map_to(Bar(), BarPydantic)) == repr(BarPydantic(x=5, y="some_default", z=1))


def test_pydantic_defaults_with_IGNORE_MISSING_MAPPING():
    with pytest.deprecated_call():

        @mapper(
            BarPydantic,
            {"x": IGNORE_MISSING_MAPPING, "y": IGNORE_MISSING_MAPPING, "z": IGNORE_MISSING_MAPPING},
        )
        class Bar(BaseModel):
            pass

        assert repr(map_to(Bar(), BarPydantic)) == repr(BarPydantic(x=5, y="some_default", z=1))


@dataclass
class BarDataclass:
    x: int = field(default=5)
    y: str = "some_default"
    z: int = field(default_factory=lambda: 1)


def test_dataclass_defaults():
    @mapper(
        BarDataclass,
        {"x": init_with_default(), "y": init_with_default(), "z": init_with_default()},
    )
    @dataclass
    class Bar:
        pass

    assert map_to(Bar(), BarDataclass) == BarDataclass(x=5, y="some_default", z=1)


class FooPydantic(BaseModel):
    x: int = 42


def test_pydantic_optional_to_defaults():
    @mapper(FooPydantic)
    class Foo(BaseModel):
        x: Optional[int]

    assert repr(map_to(Foo(x=5), FooPydantic)) == repr(FooPydantic(x=5))
    assert repr(map_to(Foo(x=None), FooPydantic)) == repr(FooPydantic(x=42))


@dataclass
class FooDataclass:
    x: int = 42


def test_dataclass_optional_to_defaults():
    @mapper(FooDataclass)
    @dataclass
    class Foo:
        x: Optional[int]

    assert repr(map_to(Foo(x=5), FooDataclass)) == repr(FooDataclass(x=5))
    assert repr(map_to(Foo(x=None), FooDataclass)) == repr(FooDataclass(x=42))


class ATo(BaseModel):
    x: int


class BTo(BaseModel):
    aa: List[ATo] = Field(default_factory=list)


def test_pydantic_optional_list_to_defaults():
    @mapper(ATo)
    class A(BaseModel):
        x: int

    @mapper(BTo)
    class B(BaseModel):
        aa: Optional[List[A]]

    assert repr(map_to(B(aa=[A(x=42)]), BTo)) == repr(BTo(aa=[ATo(x=42)]))
    assert repr(map_to(B(aa=None), BTo)) == repr(BTo(aa=[]))


class OptionalWithNoneDefaultPydantic(BaseModel):
    x: Optional[int] = None


def test_pydantic_optional_with_none_default():
    @mapper(OptionalWithNoneDefaultPydantic, {"x": init_with_default()})
    class Foo(BaseModel):
        pass

    assert repr(map_to(Foo(), OptionalWithNoneDefaultPydantic)) == repr(
        OptionalWithNoneDefaultPydantic(x=None)
    )


@dataclass
class OptionalWithNoneDefaultDataclass:
    x: Optional[int] = None


def test_dataclass_optional_with_none_default():
    @mapper(OptionalWithNoneDefaultDataclass, {"x": init_with_default()})
    @dataclass
    class Foo:
        pass

    assert map_to(Foo(), OptionalWithNoneDefaultDataclass) == OptionalWithNoneDefaultDataclass(
        x=None
    )


@dataclass
class RequiredField:
    x: int


def test_dataclass_init_with_default_for_required_field():
    with pytest.raises(ValueError) as excinfo:

        @mapper(RequiredField, {"x": init_with_default()})
        @dataclass
        class Foo:
            pass

    assert (
        str(excinfo.value)
        == "'x' of 'RequiredField' cannot be set to init_with_default(), as it has no default"
    )

    with pytest.deprecated_call(), pytest.raises(ValueError) as excinfo:

        @mapper(RequiredField, {"x": IGNORE_MISSING_MAPPING})
        @dataclass
        class Foo2:
            pass

    assert (
        str(excinfo.value)
        == "'x' of 'RequiredField' cannot be set to IGNORE_MISSING_MAPPING, as it has no default"
    )
