from pydantic import BaseModel

from safe_mapper.safe_mapper import map_to, safe_mapper_from


class Bar(BaseModel):
    x: int
    y: str


def test_pydantic_defaults():
    @safe_mapper_from(Bar, {"name": "y"})
    class Foo(BaseModel):
        x: int
        name: str

    assert repr(map_to(Bar(x=42, y="Anne"), Foo)) == repr(Foo(x=42, name="Anne"))
