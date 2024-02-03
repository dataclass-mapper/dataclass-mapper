from dataclasses import dataclass
from typing import Any

from dataclass_mapper.mapper import map_to, mapper


def test_dataclass_any():
    @dataclass
    class Target:
        x: Any

    @mapper(Target)
    @dataclass
    class Source:
        x: int

    assert map_to(Source(x=42), Target) == Target(x=42)

    target = Target(42)
    map_to(Source(x=5), target)
    assert target == Target(5)
