from dataclasses import dataclass

import pytest

from dataclass_mapper import from_extra, map_to, mapper


def test_from_extra_simple():
    @dataclass
    class Target:
        x: int

    @mapper(Target, {"x": from_extra("x")})
    @dataclass
    class Source:
        pass

    assert map_to(Source(), Target, {"x": 42}) == Target(x=42)


def test_from_extra_missing_extra():
    @dataclass
    class Target:
        x: int

    @mapper(Target, {"x": from_extra("x")})
    @dataclass
    class Source:
        pass

    with pytest.raises(TypeError) as excinfo:
        map_to(Source(), Target)
    assert (
        "When mapping an object of 'Source' to 'Target' the item 'x' needs to be provided in the `extra` dictionary"
        == str(excinfo.value)
    )


def test_from_extra_recursive_simple():
    @dataclass
    class Target:
        x: int

    @mapper(Target, {"x": from_extra("x")})
    @dataclass
    class Source:
        pass

    @dataclass
    class TargetCollection:
        field: Target

    @mapper(TargetCollection)
    @dataclass
    class SourceCollection:
        field: Source

    source_collection = SourceCollection(field=Source())
    target_collection = TargetCollection(field=Target(x=1))

    assert map_to(source_collection, TargetCollection, extra={"x": 1}) == target_collection
