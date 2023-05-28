import sys
from typing import Optional, Union

import pytest
from pydantic import BaseModel

from dataclass_mapper import map_to, mapper


@pytest.mark.skipif(sys.version_info < (3, 10), reason="Union types are introduced for Python 3.10")
def test_different_union_mapper():
    class Bar(BaseModel):
        x: int | float  # type: ignore[syntax]

    with pytest.raises(TypeError) as excinfo:

        @mapper(Bar)
        class DifferentUnion(BaseModel):
            x: int | str  # type: ignore[syntax]

    assert (
        "'x' of type 'Union[int, str]' of 'DifferentUnion'" " cannot be converted to 'x' of type 'Union[int, float]'"
    ) in str(excinfo.value)

    with pytest.raises(TypeError) as excinfo:

        @mapper(Bar)
        class SuperUnion(BaseModel):
            x: bool | int | float  # type: ignore[syntax]

    assert (
        "'x' of type 'Union[bool, int, float]' of 'SuperUnion'"
        " cannot be converted to 'x' of type 'Union[int, float]'"
    ) in str(excinfo.value)


def test_sub_unions():
    class Bar(BaseModel):
        x: Union[float, str]
        y: Union[float, str]
        z: Union[bool, float, str]
        a: Union[int, float, None]

    @mapper(Bar)
    class Foo(BaseModel):
        x: float
        y: Union[float, str]
        z: Union[bool, str]
        a: Optional[int]

    foo = Foo(x=1.2, y="abc", z=True, a=5)
    bar = Bar(x=1.2, y="abc", z=True, a=5)
    assert map_to(foo, Bar) == bar
