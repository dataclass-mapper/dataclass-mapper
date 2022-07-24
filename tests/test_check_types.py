from dataclasses import dataclass

import pytest

from dataclass_mapper.mapper import map_to, mapper


@dataclass
class Bar:
    x: int
    y: str


def test_check_normal_types():
    with pytest.raises(TypeError) as excinfo:

        @mapper(Bar, {"x": "y", "y": "x"})
        @dataclass
        class Foo:
            x: int
            y: str

    possible_errors = [
        "'x' of type 'int' of 'Foo' cannot be converted to 'y' of type 'str'",
        "'y' of type 'str' of 'Foo' cannot be converted to 'x' of type 'int'",
    ]
    assert any(p in str(excinfo.value) for p in possible_errors)
