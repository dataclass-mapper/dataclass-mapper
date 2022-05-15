from dataclasses import dataclass

import pytest

from safe_mapper.safe_mapper import map_to, safe_mapper


@dataclass
class Bar:
    x: int
    y: str


@dataclass
class Person:
    first_name: str
    second_name: str
    age: int


def test_simple_mapper():
    @safe_mapper(Bar, {"x": "x", "y": "y"})
    @dataclass
    class Foo:
        x: int
        y: str

    foo = Foo(x=42, y="answer")
    bar = Bar(x=42, y="answer")
    assert map_to(foo, Bar) == bar


def test_default_arg_mapper():
    @safe_mapper(Bar, {"x": "x"})
    @dataclass
    class Foo:
        x: int
        y: str

    foo = Foo(x=42, y="answer")
    bar = Bar(x=42, y="answer")
    assert map_to(foo, Bar) == bar

    @safe_mapper(Bar)
    @dataclass
    class Foo2:
        x: int
        y: str

    foo2 = Foo2(x=42, y="answer")
    bar2 = Bar(x=42, y="answer")
    assert map_to(foo2, Bar) == bar2


def test_cyclic_mapper():
    @safe_mapper(Bar, {"x": "answer", "y": "of_what"})
    @dataclass
    class FooOtherOrder:
        of_what: str
        answer: int

    foo = FooOtherOrder(of_what="everything", answer=42)
    bar = Bar(x=42, y="everything")
    assert map_to(foo, Bar) == bar


def test_forgotten_target_mapping():
    with pytest.raises(ValueError) as excinfo:

        @safe_mapper(Person, {"first_name": "x"})
        @dataclass
        class ForgottenMapping:
            x: str
            age: int

    assert "'second_name' of 'Person' has no mapping in 'ForgottenMapping'" in str(excinfo.value)


def test_additional_key():
    with pytest.raises(ValueError) as excinfo:

        @safe_mapper(Person, {"first_name": "first", "second_name": "second", "height": ""})
        @dataclass
        class AdditionalKeyMapping:
            first: str
            second: str
            age: int

    assert "'height' of mapping in 'AdditionalKeyMapping' doesn't exist in 'Person" in str(
        excinfo.value
    )


def test_Readme_example():
    @safe_mapper(Person, {"second_name": "surname"})
    @dataclass
    class Contact:
        first_name: str
        surname: str
        age: int

    contact = Contact(first_name="Shakil", surname="Casey", age=35)
    person = map_to(contact, Person)
    assert person == Person(first_name="Shakil", second_name="Casey", age=35)
