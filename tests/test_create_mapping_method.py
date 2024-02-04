from textwrap import dedent

import pytest

from dataclass_mapper.fieldtypes import ClassFieldType
from dataclass_mapper.implementations.base import FieldMeta
from dataclass_mapper.implementations.dataclasses import DataclassClassMeta
from dataclass_mapper.mapping_method import CreateMappingMethodSourceCode, FromExtra
from tests.utils import assert_ast_equal


def prepare_expected_code(code: str) -> str:
    """remove empty lines and dedent"""
    return "\n".join(line for line in dedent(code).split("\n") if line)


@pytest.fixture
def code() -> CreateMappingMethodSourceCode:
    return CreateMappingMethodSourceCode(
        source_cls=DataclassClassMeta(
            name="Source",
            fields={},
            clazz=None,
            internal_name="Source",
        ),
        target_cls=DataclassClassMeta(
            name="Target",
            fields={},
            clazz=None,
            internal_name="TargetAlias",
        ),
    )


def test_code_gen_add_normal_assignment(code: CreateMappingMethodSourceCode) -> None:
    code.add_mapping(
        target=FieldMeta(
            attribute_name="target_x", type=ClassFieldType(int), required=True, initializer_param_name="target_x"
        ),
        source=FieldMeta(
            attribute_name="source_x", type=ClassFieldType(int), required=True, initializer_param_name="source_x"
        ),
    )
    expected_code = prepare_expected_code(
        """
        def convert(self, extra: "dict") -> "Target":
            d = {}
            d["target_x"] = self.source_x
            return TargetAlias(**d)
        """
    )
    assert_ast_equal(code.get_ast(), expected_code)


def test_code_gen_alias(code: CreateMappingMethodSourceCode) -> None:
    code.add_mapping(
        target=FieldMeta(
            attribute_name="target_x", type=ClassFieldType(int), required=True, initializer_param_name="TARGET_X"
        ),
        source=FieldMeta(
            attribute_name="source_x", type=ClassFieldType(int), required=True, initializer_param_name="source_x"
        ),
    )
    expected_code = prepare_expected_code(
        """
        def convert(self, extra: "dict") -> "Target":
            d = {}
            d["TARGET_X"] = self.source_x
            return TargetAlias(**d)
        """
    )
    assert_ast_equal(code.get_ast(), expected_code)


def test_bypass_validators_option_disabled_for_dataclasses() -> None:
    code = CreateMappingMethodSourceCode(
        source_cls=DataclassClassMeta(
            name="Source",
            fields={},
            clazz=None,
            internal_name="Source",
        ),
        target_cls=DataclassClassMeta(
            name="Target",
            fields={},
            clazz=None,
            internal_name="TargetAlias",
        ),
    )
    expected_code = prepare_expected_code(
        """
        def convert(self, extra: "dict") -> "Target":
            d = {}
            return TargetAlias(**d)
        """
    )
    assert_ast_equal(code.get_ast(), expected_code)


def test_provide_with_extra_code_check(code: CreateMappingMethodSourceCode):
    code.add_from_extra(
        target=FieldMeta(
            attribute_name="target_x", type=ClassFieldType(int), required=True, initializer_param_name="target_x"
        ),
        source=FromExtra("external_x"),
    )
    expected_code = prepare_expected_code(
        """
        def convert(self, extra: "dict") -> "Target":
            d = {}
            if "external_x" not in extra:
                raise TypeError("When mapping an object of 'Source' to 'Target' the item 'external_x' needs to be provided in the `extra` dictionary")
            d["target_x"] = extra["external_x"]
            return TargetAlias(**d)
        """  # noqa: E501
    )
    assert_ast_equal(code.get_ast(), expected_code)
