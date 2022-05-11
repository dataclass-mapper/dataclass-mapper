from dataclasses import dataclass
from safe_mapper.safe_mapper import safe_mapper, safe_convert

import pytest


@dataclass
class Bar:
    x: int
    y: str


@dataclass
class Name:
    first_name: str
    second_name: str


def test_simple_mapper():
    @safe_mapper(Bar, {"x": "x", "y": "y"})
    @dataclass
    class Foo:
        x: int
        y: str

    foo = Foo(x=42, y="answer")
    bar = Bar(x=42, y="answer")
    assert safe_convert(foo) == bar


def test_default_arg_mapper():
    @safe_mapper(Bar, {"x": "x"})
    @dataclass
    class Foo:
        x: int
        y: str

    foo = Foo(x=42, y="answer")
    bar = Bar(x=42, y="answer")
    assert safe_convert(foo) == bar

    @safe_mapper(Bar)
    @dataclass
    class Foo2:
        x: int
        y: str

    foo2 = Foo2(x=42, y="answer")
    bar2 = Bar(x=42, y="answer")
    assert safe_convert(foo2) == bar2


def test_cyclic_mapper():
    @safe_mapper(Bar, {"x": "answer", "y": "of_what"})
    @dataclass
    class FooOtherOrder:
        of_what: str
        answer: int

    foo = FooOtherOrder(of_what="everything", answer=42)
    bar = Bar(x=42, y="everything")
    assert safe_convert(foo) == bar


def test_forgotten_target_mapping():
    with pytest.raises(ValueError) as excinfo:

        @safe_mapper(Name, {"first_name": "x"})
        @dataclass
        class ForgottenMapping:
            x: str

    assert "'second_name' of 'Name' has no mapping in 'ForgottenMapping'" in str(excinfo.value)


def test_additional_key():
    with pytest.raises(ValueError) as excinfo:

        @safe_mapper(Name, {"first_name": "first", "second_name": "second", "age": "age"})
        @dataclass
        class AdditionalKeyMapping:
            first: str
            second: str
            age: int

    assert "'age' of mapping in 'AdditionalKeyMapping' doesn't exist in 'Name" in str(excinfo.value)
