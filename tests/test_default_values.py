from typing import Dict

from dataclasses import dataclass

from dataclass_mapper import map_to, mapper


@dataclass
class Bar:
    x: int


def test_default_values_in_mapping():
    @mapper(Bar, {"x": lambda: 42})
    @dataclass
    class Foo:
        pass

    assert map_to(Foo(), Bar) == Bar(x=42)
