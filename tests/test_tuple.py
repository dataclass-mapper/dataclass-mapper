from dataclasses import dataclass
from typing import Tuple

from dataclass_mapper.mapper import map_to, mapper


def test_rec_tuple():
    @dataclass
    class ATarget:
        x: int

    @mapper(ATarget)
    @dataclass
    class ASource:
        x: int

    @dataclass
    class BTarget:
        x: int

    @mapper(BTarget)
    @dataclass
    class BSource:
        x: int

    @dataclass
    class Target:
        item: Tuple[ATarget, BTarget, str]

    @mapper(Target)
    @dataclass
    class Source:
        item: Tuple[ASource, BSource, str]

    source = Source(item=(ASource(5), BSource(42), "foo"))
    assert map_to(source, Target) == Target(item=(ATarget(5), BTarget(42), "foo"))
