from sys import version_info
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import pytest

from dataclass_mapper.fieldtypes import (
    ClassFieldType,
    DictFieldType,
    FieldType,
    ListFieldType,
    OptionalFieldType,
    SetFieldType,
    UnionFieldType,
    compute_field_type,
)


def test_not_same_type_comparisons():
    assert ClassFieldType(int) != OptionalFieldType(ClassFieldType(int))
    assert OptionalFieldType(ClassFieldType(int)) != ClassFieldType(int)
    assert SetFieldType(ClassFieldType(int)) != ClassFieldType(int)
    assert ListFieldType(ClassFieldType(int)) != ClassFieldType(int)
    assert UnionFieldType([ClassFieldType(int), ClassFieldType(float)]) != ClassFieldType(int)
    assert DictFieldType(ClassFieldType(int), ClassFieldType(float)) != ClassFieldType(int)


class Foo:
    pass


class Bar:
    pass


TEST_DATA: List[Tuple[Any, FieldType, str]] = [
    (int, ClassFieldType(int), "int"),
    (float, ClassFieldType(float), "float"),
    (Optional[int], OptionalFieldType(ClassFieldType(int)), "Optional[int]"),
    (Union[int, float], UnionFieldType([ClassFieldType(int), ClassFieldType(float)]), "Union[int, float]"),
    (
        Optional[Union[int, float]],
        OptionalFieldType(UnionFieldType([ClassFieldType(int), ClassFieldType(float)])),
        "Union[int, float, None]",
    ),
    (
        Union[int, float, None],
        OptionalFieldType(UnionFieldType([ClassFieldType(int), ClassFieldType(float)])),
        "Union[int, float, None]",
    ),
    (
        Bar,
        ClassFieldType(Bar),
        "Bar",
    ),
    (
        List[Bar],
        ListFieldType(ClassFieldType(Bar)),
        "List[Bar]",
    ),
    (
        Dict[Bar, Optional[List[Optional[Foo]]]],
        DictFieldType(
            ClassFieldType(Bar),
            OptionalFieldType(ListFieldType(OptionalFieldType(ClassFieldType(Foo)))),
        ),
        "Dict[Bar, Optional[List[Optional[Foo]]]]",
    ),
    (
        Set[Bar],
        SetFieldType(ClassFieldType(Bar)),
        "Set[Bar]",
    ),
]


if version_info >= (3, 10):
    TEST_DATA.extend(
        [
            (
                int | float,  # type: ignore
                UnionFieldType([ClassFieldType(int), ClassFieldType(float)]),
                "Union[int, float]",
            ),
            (
                int | float | None,  # type: ignore
                OptionalFieldType(UnionFieldType([ClassFieldType(int), ClassFieldType(float)])),
                "Union[int, float, None]",
            ),
            (
                dict[Foo, Bar],  # type: ignore
                DictFieldType(ClassFieldType(Foo), ClassFieldType(Bar)),
                "Dict[Foo, Bar]",
            ),
            (
                list[Foo | None],  # type: ignore
                ListFieldType(OptionalFieldType(ClassFieldType(Foo))),
                "List[Optional[Foo]]",
            ),
        ]
    )


@pytest.mark.parametrize(["type_", "expected_parsed", "expected_str"], TEST_DATA)
def test_check_field_name_parsing_and_str(type_: Any, expected_parsed: FieldType, expected_str: str):
    field_type = compute_field_type(type_)
    assert field_type == expected_parsed
    assert str(field_type) == expected_str


@pytest.mark.skipif(version_info < (3, 10), reason="Union Syntax")
def test_get_class_name_for_non_class():
    field_type = ClassFieldType(int | float)  # type: ignore
    assert str(field_type)
