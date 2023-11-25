from textwrap import dedent

import pytest

from dataclass_mapper.fieldtypes import ClassFieldType
from dataclass_mapper.implementations.base import FieldMeta
from dataclass_mapper.implementations.dataclasses import DataclassClassMeta
from dataclass_mapper.mapping_method import CreateMappingMethodSourceCode, FromExtra


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
            alias_name="Source",
        ),
        target_cls=DataclassClassMeta(
            name="Target",
            fields={},
            clazz=None,
            alias_name="TargetAlias",
        ),
    )


def test_code_gen_add_normal_assignment(code: CreateMappingMethodSourceCode) -> None:
    code.add_mapping(
        target=FieldMeta(name="target_x", type=ClassFieldType(int), required=True),
        source=FieldMeta(name="source_x", type=ClassFieldType(int), required=True),
    )
    expected_code = prepare_expected_code(
        """
        def convert(self, extra: dict) -> "Target":
            d = {}
            d["target_x"] = self.source_x
            return TargetAlias(**d)
        """
    )
    assert str(code) == expected_code


# def test_code_gen_add_assignment_only_if_not_None(code: CreateMappingMethodSourceCode) -> None:
#     code.add_mapping(
#         target=FieldMeta(name="target_x", type=int, allow_none=False, required=False),
#         source=FieldMeta(name="source_x", type=int, allow_none=True, required=True),
#     )
#     expected_code = prepare_expected_code(
#         """
#         def convert(self, extra: dict) -> "Target":
#             d = {}
#             if self.source_x is not None:
#                 d["target_x"] = self.source_x
#             return TargetAlias(**d)
#         """
#     )
#     assert str(code) == expected_code


def test_bypass_validators_option_disabled_for_dataclasses() -> None:
    code = CreateMappingMethodSourceCode(
        source_cls=DataclassClassMeta(
            name="Source",
            fields={},
            clazz=None,
            alias_name="Source",
        ),
        target_cls=DataclassClassMeta(
            name="Target",
            fields={},
            clazz=None,
            alias_name="TargetAlias",
        ),
    )
    expected_code = prepare_expected_code(
        """
        def convert(self, extra: dict) -> "Target":
            d = {}
            return TargetAlias(**d)
        """
    )
    assert str(code) == expected_code


def test_provide_with_extra_code_check(code: CreateMappingMethodSourceCode):
    code.add_from_extra(target=FieldMeta(name="target_x", type=ClassFieldType(int), required=True), source=FromExtra("external_x"))
    expected_code = prepare_expected_code(
        """
        def convert(self, extra: dict) -> "Target":
            d = {}
            if "external_x" not in extra:
                raise TypeError("When mapping an object of 'Source' to 'Target' the item 'external_x' needs to be provided in the `extra` dictionary")
            d["target_x"] = extra["external_x"]
            return TargetAlias(**d)
        """  # noqa: E501
    )
    assert str(code) == expected_code
