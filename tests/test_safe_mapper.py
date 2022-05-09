from dataclasses import dataclass
from safe_mapper.safe_mapper import SafeMapper, safe_convert


@dataclass
class Bar:
    x: int
    y: str


@dataclass
class Foo(metaclass=SafeMapper):
    x: int
    y: str

    class Config:
        mapping_target_class = Bar
        mapping = {
            "x": "x",
            "y": "y",
        }


def test_simple_mapper():
    foo = Foo(x=42, y="answer")
    bar = Bar(x=42, y="answer")
    assert safe_convert(foo) == bar


@dataclass
class FooOtherOrder(metaclass=SafeMapper):
    of_what: str
    answer: int

    class Config:
        mapping_target_class = Bar
        mapping = {
            "x": "answer",
            "y": "of_what",
        }


def test_cyclic_mapper():
    foo = FooOtherOrder(of_what="everything", answer=42)
    bar = Bar(x=42, y="everything")
    assert safe_convert(foo) == bar
