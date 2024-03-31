from dataclasses import dataclass

import pytest

from dataclass_mapper.collection import COLLECTION
from dataclass_mapper.mapper import create_mapper


def test_is_mappable_to():
    @dataclass
    class Foo:
        pass

    @dataclass
    class Bar:
        pass

    create_mapper(Foo, Bar)

    assert COLLECTION.contains_create(Foo, Bar)
    assert not COLLECTION.contains_create(Bar, Foo)
    assert not COLLECTION.contains_create(int, int)


def test_is_updatable_to():
    @dataclass
    class Foo:
        pass

    @dataclass
    class Bar:
        pass

    create_mapper(Foo, Bar)

    assert COLLECTION.contains_update(Foo, Bar)
    assert not COLLECTION.contains_update(Bar, Foo)
    assert not COLLECTION.contains_update(int, int)


def test_naming_for_object_fails():
    with pytest.raises(TypeError):
        assert COLLECTION.get_create_code(5, 5)  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        assert COLLECTION.get_update_code(5, 5)  # type: ignore[arg-type]
