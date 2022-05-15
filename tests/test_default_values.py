from dataclasses import dataclass

from safe_mapper import map_to, safe_mapper


@dataclass
class Bar:
    x: int


def test_default_values_in_mapping():
    @safe_mapper(Bar, {"x": lambda: 42})
    @dataclass
    class Foo:
        pass

    assert map_to(Foo(), Bar) == Bar(x=42)
