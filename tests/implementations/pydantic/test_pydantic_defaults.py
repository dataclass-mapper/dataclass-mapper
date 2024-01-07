from typing import Optional

import pytest

from dataclass_mapper import IGNORE_MISSING_MAPPING, USE_DEFAULT, init_with_default, map_to, mapper
from dataclass_mapper.implementations.pydantic_v1 import pydantic_version

if pydantic_version()[0] != 1:
    pytest.skip("V1 validators syntax", allow_module_level=True)

from pydantic import BaseModel, Field


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


def test_pydantic_optional_with_none_default():
    class OptionalWithNoneDefaultPydantic(BaseModel):
        x: Optional[int] = None

    @mapper(OptionalWithNoneDefaultPydantic, {"x": init_with_default()})
    class Foo(BaseModel):
        pass

    assert repr(map_to(Foo(), OptionalWithNoneDefaultPydantic)) == repr(OptionalWithNoneDefaultPydantic(x=None))
