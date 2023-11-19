from sys import version_info
from typing import Any, Dict, List, Optional, Tuple, Union

import pytest

from dataclass_mapper.fieldtypes import (
    ClassFieldType,
    DictFieldType,
    FieldType,
    ListFieldType,
    OptionalFieldType,
    UnionFieldType,
    compute_field_type,
)


class Foo:
    pass


class Bar:
    pass


TEST_DATA: List[Tuple[Any, FieldType, str]] = [
    (int, ClassFieldType(int), "int"),
    (float, ClassFieldType(float), "float"),
    (Optional[int], OptionalFieldType(..., inner=[ClassFieldType(int)]), "Optional[int]"),
    (Union[int, float], UnionFieldType(..., inner=[ClassFieldType(int), ClassFieldType(float)]), "Union[int, float]"),
    (
        Optional[Union[int, float]],
        OptionalFieldType(..., inner=[UnionFieldType(..., inner=[ClassFieldType(int), ClassFieldType(float)])]),
        "Union[int, float, None]",
    ),
    (
        Union[int, float, None],
        OptionalFieldType(..., inner=[UnionFieldType(..., inner=[ClassFieldType(int), ClassFieldType(float)])]),
        "Union[int, float, None]",
    ),
    (Bar, ClassFieldType(Bar), "Bar"),
    (List[Bar], ListFieldType(..., inner=[ClassFieldType(Bar)]), "List[Bar]"),
    (
        Dict[Bar, Optional[List[Optional[Foo]]]],
        DictFieldType(
            ...,
            [
                ClassFieldType(Bar),
                OptionalFieldType(..., [ListFieldType(..., [OptionalFieldType(..., [ClassFieldType(Foo)])])]),
            ],
        ),
        "Dict[Bar, Optional[List[Optional[Foo]]]]",
    ),
]


if version_info >= (3, 9):
    TEST_DATA.extend([
        (int | float, UnionFieldType(..., [ClassFieldType(int), ClassFieldType(float)]), "Union[int, float]"),
        (int | float | None, OptionalFieldType(..., [UnionFieldType(..., [ClassFieldType(int), ClassFieldType(float)])]), "Union[int, float, None]"),
        (dict[Foo, Bar], DictFieldType(..., [ClassFieldType(Foo), ClassFieldType(Bar)]), "Dict[Foo, Bar]"),
        (list[Foo | None], ListFieldType(..., [OptionalFieldType(..., [ClassFieldType(Foo)])]), "List[Optional[Foo]]"),
    ])


@pytest.mark.parametrize(["type_", "expected_parsed", "expected_str"], TEST_DATA)
def test_check_field_name_parsing_and_str(type_: Any, expected_parsed: FieldType, expected_str: str):
    field_type = compute_field_type(type_)
    assert field_type == expected_parsed
    assert str(field_type) == expected_str
