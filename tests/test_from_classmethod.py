from typing import List

from pydantic import BaseModel

from dataclass_mapper.mapper import map_to, mapper_from


def test_pydantic_from():
    class BarFrom(BaseModel):
        x: int
        y: str

    @mapper_from(BarFrom, {"name": "y"})
    class Bar(BaseModel):
        x: int
        name: str

    assert repr(map_to(BarFrom(x=42, y="Anne"), Bar)) == repr(Bar(x=42, name="Anne"))


def test_pydantic_from_rec_list():
    class BarFrom(BaseModel):
        x: int
        y: str

    class RecFrom(BaseModel):
        bars: List[BarFrom]
        bar: BarFrom

    @mapper_from(BarFrom, {"name": "y"})
    class Bar(BaseModel):
        x: int
        name: str

    @mapper_from(RecFrom)
    class Rec(BaseModel):
        bars: List[Bar]

    bar: Bar
    bar_from = BarFrom(x=42, y="Anne")
    bar = Bar(x=42, name="Anne")
    assert repr(map_to(RecFrom(bar=bar_from, bars=[bar_from]), Rec)) == repr(Rec(bar=bar, bars=[bar]))
