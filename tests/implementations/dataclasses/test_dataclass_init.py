from dataclasses import dataclass, field

from dataclass_mapper import map_to, mapper


def test_dataclass_field_init_False():
    @dataclass
    class Target:
        x: int
        y: int = field(init=False)

        def __post_init__(self):
            self.y = self.x + 1

    @mapper(Target)
    @dataclass
    class Source:
        x: int

    assert map_to(Source(5), Target).y == 6
