import sys

import pytest
from pydantic import BaseModel

from dataclass_mapper import mapper


@pytest.mark.skipif(sys.version_info < (3, 10), reason="Union types are introduced for Python 3.10")
def test_differnt_union_mapper():
    class Bar(BaseModel):
        x: float | int  # type: ignore[syntax]

    with pytest.raises(TypeError) as excinfo:

        @mapper(Bar)
        class Foo(BaseModel):
            x: float | str  # type: ignore[syntax]

    assert "'x' of type 'float | str' of 'Foo' cannot be converted to 'x' of type 'float | int'" in str(excinfo.value)
