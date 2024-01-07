from dataclasses import dataclass

import pytest

from dataclass_mapper.mapper import create_mapper
from dataclass_mapper.utils import get_map_to_func_name, get_mapupdate_to_func_name, is_mappable_to, is_updatable_to


def test_is_mappable_to():
    @dataclass
    class Foo:
        pass

    @dataclass
    class Bar:
        pass

    create_mapper(Foo, Bar)

    assert is_mappable_to(Foo, Bar)
    assert not is_mappable_to(Bar, Foo)


def test_is_updabtable_to():
    @dataclass
    class Foo:
        pass

    @dataclass
    class Bar:
        pass

    create_mapper(Foo, Bar)

    assert is_updatable_to(Foo, Bar)
    assert not is_updatable_to(Bar, Foo)


def test_naming_for_object_fails():
    with pytest.raises(TypeError):
        assert get_map_to_func_name(5)

    with pytest.raises(TypeError):
        assert get_mapupdate_to_func_name(5)
