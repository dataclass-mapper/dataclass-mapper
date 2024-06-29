import sys
from dataclasses import dataclass

import pytest

from dataclass_mapper.collection import COLLECTION
from dataclass_mapper.mapper import create_mapper
from dataclass_mapper.namespace import get_namespace
from dataclass_mapper.utils import TypeAnnotation, extract_function_types


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


def test_extract_function_types():
    assert extract_function_types(lambda x: 42) == TypeAnnotation(None, None)

    def only_param(x: int):
        return 42

    assert extract_function_types(only_param) == TypeAnnotation(int, None)

    def only_return_type(x) -> int:
        return 42

    assert extract_function_types(only_return_type) == TypeAnnotation(None, int)

    def both_param_and_return_type(x: float) -> str:
        return "42"

    assert extract_function_types(both_param_and_return_type) == TypeAnnotation(float, str)

    def no_param() -> str:
        return "42"

    assert extract_function_types(no_param) == TypeAnnotation(None, str)

    def distinguish_none_type(x: None) -> None:
        pass

    if sys.version_info < (3, 10):
        NoneType = type(None)
    else:
        from types import NoneType

    assert extract_function_types(distinguish_none_type) == TypeAnnotation(NoneType, NoneType)

    def understand_string_annotations(x: "int") -> "str":
        return "42"

    assert extract_function_types(understand_string_annotations) == TypeAnnotation(int, str)

    class Foo:
        pass

    def classes(x: "Foo") -> Foo:
        return x

    namespace = get_namespace(1)

    assert extract_function_types(classes, namespace=namespace) == TypeAnnotation(Foo, Foo)

    class CallableObject:
        def __call__(self, x: int) -> str:
            return "42"

    assert extract_function_types(CallableObject()) == TypeAnnotation(int, str)

    class CallableObjectWithoutParam:
        def __call__(self) -> str:
            return "42"

    assert extract_function_types(CallableObjectWithoutParam()) == TypeAnnotation(None, str)

    # TODO: check for bad annotations that are unparsable

    # def bad_annotation(x: 1+1) -> "abcdef":
    #     pass

    # assert extract_function_types(bad_annotation) == (None, str)
