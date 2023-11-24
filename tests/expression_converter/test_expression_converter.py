from dataclasses import dataclass
from typing import List

import pytest

from dataclass_mapper.code_generator import AttributeLookup
from dataclass_mapper.expression_converters.expression_converter import map_expression
from dataclass_mapper.fieldtypes import ClassFieldType, ListFieldType, OptionalFieldType
from dataclass_mapper.fieldtypes.base import FieldType
from dataclass_mapper.fieldtypes.dict import DictFieldType
from dataclass_mapper.utils import get_map_to_func_name


@dataclass
class Foo:
    pass


@dataclass
class Bar:
    pass


int_class_field_type = ClassFieldType(int)

# mock making Foo convertable into Bar
setattr(Foo, get_map_to_func_name(Bar), lambda: Bar())


@dataclass
class Scenario:
    source: FieldType
    target: FieldType
    expected_code: str


TEST_CASES: List[Scenario] = [
    Scenario(
        source=int_class_field_type,
        target=int_class_field_type,
        expected_code="src.x",
    ),
    Scenario(
        source=OptionalFieldType(int_class_field_type),
        target=OptionalFieldType(int_class_field_type),
        expected_code="None if src.x is None else src.x",
    ),
    Scenario(
        source=ListFieldType(int_class_field_type),
        target=ListFieldType(int_class_field_type),
        # TODO: optimization potential for flat copy
        expected_code="[x for x in src.x]",
    ),
    Scenario(
        source=ListFieldType(OptionalFieldType(int_class_field_type)),
        target=ListFieldType(OptionalFieldType(int_class_field_type)),
        expected_code="[None if x is None else x for x in src.x]",
    ),
    Scenario(
        source=ListFieldType(ListFieldType(int_class_field_type)),
        target=ListFieldType(ListFieldType(int_class_field_type)),
        # TODO: don't reuse the same loop variable
        expected_code="[[x for x in x] for x in src.x]",
    ),
    Scenario(
        source=ClassFieldType(Foo),
        target=ClassFieldType(Bar),
        expected_code=f"src.x._map_to_Bar_{id(Bar)}(extra)",
    ),
    Scenario(
        source=ListFieldType(ClassFieldType(Foo)),
        target=ListFieldType(ClassFieldType(Bar)),
        expected_code=f"[x._map_to_Bar_{id(Bar)}(extra) for x in src.x]",
    ),
    Scenario(
        source=DictFieldType(ClassFieldType(Foo), ClassFieldType(Foo)),
        target=DictFieldType(ClassFieldType(Bar), ClassFieldType(Bar)),
        expected_code=f"{{k._map_to_Bar_{id(Bar)}(extra): v._map_to_Bar_{id(Bar)}(extra) for k, v in src.x.items()}}",
    ),
    Scenario(
        source=DictFieldType(ClassFieldType(Foo), OptionalFieldType(ClassFieldType(Foo))),
        target=DictFieldType(ClassFieldType(Bar), OptionalFieldType(ClassFieldType(Bar))),
        expected_code=f"{{k._map_to_Bar_{id(Bar)}(extra): None if v is None else v._map_to_Bar_{id(Bar)}(extra) for k, v in src.x.items()}}",  # noqa: E501
    ),
]


@pytest.mark.parametrize("test_case", TEST_CASES)
def test_expression_converter(test_case: Scenario):
    source = AttributeLookup("src", "x")

    assert str(map_expression(test_case.source, test_case.target, source)) == test_case.expected_code
