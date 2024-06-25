from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

import pytest

from dataclass_mapper import create_mapper, map_to, mapper, mapper_from


def test_default_values_in_mapping():
    @dataclass
    class Bar:
        x: int
        y: str

    @mapper(Bar, {"x": lambda: 42, "y": lambda self: self.name})
    @dataclass
    class FooEmpty:
        name: str

    assert map_to(FooEmpty(name="Sally"), Bar) == Bar(x=42, y="Sally")


def test_default_values_in_mapping_from():
    @dataclass
    class BarEmpty:
        pass

    @mapper_from(BarEmpty, {"x": lambda: 42})
    @dataclass
    class Foo:
        x: int

    assert map_to(BarEmpty(), Foo) == Foo(x=42)


def test_callable_factory():
    @dataclass
    class Target:
        x: int

    class Incrementor:
        def __init__(self):
            self.value: int = 0

        def __call__(self) -> int:
            self.value += 1
            return self.value

    @mapper(Target, {"x": Incrementor()})
    @dataclass
    class Source:
        pass

    assert map_to(Source(), Target) == Target(x=1)
    assert map_to(Source(), Target) == Target(x=2)


def test_refuse_factory_with_multiple_parameters():
    @dataclass
    class Target:
        x: int

    with pytest.raises(ValueError) as excinfo:
        # purposefully wrong factory with two parameter
        @mapper(Target, {"x": lambda a, b: a + b})  # type: ignore[dict-item]
        @dataclass
        class Source:
            pass

    assert str(excinfo.value) == "'x' of 'Target' cannot be mapped using a factory with more than one parameter"


def test_function_with_types_are_accepted():
    @dataclass
    class Target:
        x: int

    def func() -> int:
        return 42

    @dataclass
    class Source:
        pass

    create_mapper(Source, Target, {"x": func})


def test_function_with_types_are_accepted_2():
    @dataclass
    class Target:
        x: int

    def func(x: "Source") -> int:
        return 42

    @dataclass
    class Source:
        pass

    create_mapper(Source, Target, {"x": func})


def test_function_with_wrong_param_type_is_rejected():
    @dataclass
    class Target:
        x: int

    def func(x: "str") -> int:
        return 42

    @dataclass
    class Source:
        pass

    with pytest.raises(TypeError) as excinfo:
        create_mapper(Source, Target, {"x": func})

    assert (
        str(excinfo.value)
        == "The first parameter of the custom conversion function for field 'x' of 'Target' needs to be of type 'Source' or a super type of it, but is of type 'str'."  # noqa: E501
    )


def test_function_with_wrong_return_type_is_rejected():
    @dataclass
    class Target:
        x: int

    def func(x: "Source") -> None:
        pass

    @dataclass
    class Source:
        pass

    with pytest.raises(TypeError) as excinfo:
        create_mapper(Source, Target, {"x": func})

    assert (
        str(excinfo.value)
        == "The return value of the custom conversion function for field 'x' of 'Target' needs to be of type 'int', but is of type 'NoneType'."  # noqa: E501
    )


def test_function_with_wrong_unmappable_return_type_is_rejected():
    @dataclass
    class Target:
        x: int

    T = TypeVar("T")

    class G(Generic[T]):
        pass

    def func(x: "Source") -> "G[int]":
        return G[int]()

    @dataclass
    class Source:
        pass

    with pytest.raises(TypeError) as excinfo:
        create_mapper(Source, Target, {"x": func})

    assert (
        str(excinfo.value)
        == "The return value of the custom conversion function for field 'x' of 'Target' needs to be of type 'int', but is of type 'G'."  # noqa: E501
    )


def test_function_with_param_supertype():
    @dataclass
    class Target:
        x: int

    def func(x: "SourceBase") -> int:
        return 42

    @dataclass
    class SourceBase:
        pass

    @dataclass
    class Source(SourceBase):
        pass

    create_mapper(Source, Target, {"x": func})


def test_function_with_param_subtype_is_rejected():
    @dataclass
    class Target:
        x: int

    def func(x: "Source") -> int:
        return 42

    @dataclass
    class SourceBase:
        pass

    @dataclass
    class Source(SourceBase):
        pass

    with pytest.raises(TypeError) as excinfo:
        create_mapper(SourceBase, Target, {"x": func})

    assert (
        str(excinfo.value)
        == "The first parameter of the custom conversion function for field 'x' of 'Target' needs to be of type 'SourceBase' or a super type of it, but is of type 'Source'."  # noqa: E501
    )


def test_function_with_return_subtype():
    class FooBase:
        pass

    class Foo(FooBase):
        pass

    @dataclass
    class Target:
        x: FooBase

    def func(x: "Source") -> Foo:
        return Foo()

    @dataclass
    class Source:
        pass

    create_mapper(Source, Target, {"x": func})


def test_function_with_return_supertype_is_rejected():
    class FooBase:
        pass

    class Foo(FooBase):
        pass

    @dataclass
    class Target:
        x: Foo

    def func(x: "Source") -> FooBase:
        return Foo()

    @dataclass
    class Source:
        pass

    with pytest.raises(TypeError) as excinfo:
        create_mapper(Source, Target, {"x": func})

    assert (
        str(excinfo.value)
        == "The return value of the custom conversion function for field 'x' of 'Target' needs to be of type 'Foo', but is of type 'FooBase'."  # noqa: E501
    )


def test_function_with_optional_field():
    @dataclass
    class Target:
        x: Optional[int]

    def func() -> int:
        return 42

    @dataclass
    class Source:
        pass

    create_mapper(Source, Target, {"x": func})
