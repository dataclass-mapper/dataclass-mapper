from dataclasses import dataclass, field

from pydantic import BaseModel, Field

from safe_mapper.safe_mapper import map_to, safe_mapper


class BarPydantic(BaseModel):
    x: int = Field(default=5)
    y: str = "some_default"
    z: int = Field(default_factory=lambda: 1)


def test_pydantic_defaults():
    @safe_mapper(BarPydantic)
    class Bar(BaseModel):
        pass

    assert repr(map_to(Bar(), BarPydantic)) == repr(BarPydantic(x=5, y="some_default", z=1))


@dataclass
class BarDataclass:
    x: int = field(default=5)
    y: str = "some_default"
    z: int = field(default_factory=lambda: 1)


def test_dataclass_defaults():
    @safe_mapper(BarDataclass)
    @dataclass
    class Bar:
        pass

    assert map_to(Bar(), BarDataclass) == BarDataclass(x=5, y="some_default", z=1)


# TODO: if source is optional, and target is non-optional and has a default, use the default
