from dataclasses import dataclass, field
from typing import Optional

import pytest

from dataclass_mapper import IGNORE_MISSING_MAPPING, init_with_default, map_to, mapper


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


@dataclass
class OptionalWithNoneDefaultDataclass:
    x: Optional[int] = None


def test_dataclass_optional_with_none_default():
    @mapper(OptionalWithNoneDefaultDataclass, {"x": init_with_default()})
    @dataclass
    class Foo:
        pass

    assert map_to(Foo(), OptionalWithNoneDefaultDataclass) == OptionalWithNoneDefaultDataclass(x=None)


@dataclass
class RequiredField:
    x: int


def test_dataclass_init_with_default_for_required_field():
    with pytest.raises(ValueError) as excinfo:

        @mapper(RequiredField, {"x": init_with_default()})
        @dataclass
        class Foo:
            pass

    assert str(excinfo.value) == "'x' of 'RequiredField' cannot be set to init_with_default(), as it has no default"

    with pytest.deprecated_call(), pytest.raises(ValueError) as excinfo:

        @mapper(RequiredField, {"x": IGNORE_MISSING_MAPPING})
        @dataclass
        class Foo2:
            pass

    assert str(excinfo.value) == "'x' of 'RequiredField' cannot be set to IGNORE_MISSING_MAPPING, as it has no default"
