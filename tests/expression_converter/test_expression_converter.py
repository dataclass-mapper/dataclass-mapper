from dataclasses import dataclass
from typing import List

import pytest

from dataclass_mapper.code_generator import AttributeLookup, Variable
from dataclass_mapper.collection import COLLECTION
from dataclass_mapper.expression_converters.expression_converter import map_expression
from dataclass_mapper.fieldtypes import ClassFieldType, ListFieldType, OptionalFieldType, SetFieldType
from dataclass_mapper.fieldtypes.base import FieldType
from dataclass_mapper.fieldtypes.dict import DictFieldType
from tests.utils import assert_ast_equal


@dataclass(frozen=True)
class Foo:
    pass


@dataclass(frozen=True)
class Bar:
    pass


int_class_field_type = ClassFieldType(int)

# mock making Foo convertable into Bar
COLLECTION.store_create_func(Foo, Bar, lambda: Bar(), "", {})


@dataclass
class Scenario:
    source: FieldType
    target: FieldType
    expected_code: str


FOO_TO_BAR_CREATE = f'COLLECTION["Foo_{id(Foo)}__mapcreate_to__Bar_{id(Bar)}"]'

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
        expected_code="[x0 for x0 in src.x]",
    ),
    Scenario(
        source=ListFieldType(OptionalFieldType(int_class_field_type)),
        target=ListFieldType(OptionalFieldType(int_class_field_type)),
        expected_code="[None if x0 is None else x0 for x0 in src.x]",
    ),
    Scenario(
        source=ListFieldType(ListFieldType(int_class_field_type)),
        target=ListFieldType(ListFieldType(int_class_field_type)),
        expected_code="[[x1 for x1 in x0] for x0 in src.x]",
    ),
    Scenario(
        source=ClassFieldType(Foo),
        target=ClassFieldType(Bar),
        expected_code=f"{FOO_TO_BAR_CREATE}(src.x, extra)",
    ),
    Scenario(
        source=ListFieldType(ClassFieldType(Foo)),
        target=ListFieldType(ClassFieldType(Bar)),
        expected_code=f"[{FOO_TO_BAR_CREATE}(x0, extra) for x0 in src.x]",
    ),
    Scenario(
        source=DictFieldType(ClassFieldType(Foo), ClassFieldType(Foo)),
        target=DictFieldType(ClassFieldType(Bar), ClassFieldType(Bar)),
        expected_code=f"{{{FOO_TO_BAR_CREATE}(k0, extra): {FOO_TO_BAR_CREATE}(v0, extra) for (k0, v0) in src.x.items()}}",  # noqa: E501
    ),
    Scenario(
        source=DictFieldType(ClassFieldType(Foo), OptionalFieldType(ClassFieldType(Foo))),
        target=DictFieldType(ClassFieldType(Bar), OptionalFieldType(ClassFieldType(Bar))),
        expected_code=f"{{{FOO_TO_BAR_CREATE}(k0, extra): None if v0 is None else {FOO_TO_BAR_CREATE}(v0, extra) for (k0, v0) in src.x.items()}}",  # noqa: E501
    ),
    Scenario(
        source=SetFieldType(ClassFieldType(Foo)),
        target=SetFieldType(ClassFieldType(Bar)),
        expected_code=f"{{{FOO_TO_BAR_CREATE}(x0, extra) for x0 in src.x}}",
    ),
]


@pytest.mark.parametrize("test_case", TEST_CASES)
def test_expression_converter(test_case: Scenario):
    source = AttributeLookup(Variable("src"), "x")

    assert_ast_equal(
        map_expression(test_case.source, test_case.target, source, 0).generate_ast(), test_case.expected_code
    )
