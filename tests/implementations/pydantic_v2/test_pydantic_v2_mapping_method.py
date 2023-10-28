from textwrap import dedent

import pytest

from dataclass_mapper.implementations.base import FieldMeta
from dataclass_mapper.implementations.dataclasses import DataclassClassMeta
from dataclass_mapper.implementations.pydantic_v2 import PydanticV2ClassMeta
from dataclass_mapper.mapping_method import CreateMappingMethodSourceCode


def prepare_expected_code(code: str) -> str:
    """remove empty lines and dedent"""
    return "\n".join(line for line in dedent(code).split("\n") if line)


@pytest.fixture
def code() -> CreateMappingMethodSourceCode:
    return CreateMappingMethodSourceCode(
        source_cls=DataclassClassMeta(
            name="Source",
            fields={},
            alias_name="Source",
        ),
        target_cls=DataclassClassMeta(
            name="Target",
            fields={},
            alias_name="TargetAlias",
        ),
    )


def test_bypass_validators_option_for_pydantic() -> None:
    code = CreateMappingMethodSourceCode(
        source_cls=PydanticV2ClassMeta(
            name="Source",
            fields={},
            use_construct=False,
            alias_name="Source",
        ),
        target_cls=PydanticV2ClassMeta(
            name="Target",
            fields={},
            use_construct=True,
            alias_name="TargetAlias",
        ),
    )
    expected_code = prepare_expected_code(
        """
        def convert(self, extra: dict) -> "Target":
            d = {}
            return TargetAlias.model_construct(**d)
        """
    )
    assert str(code) == expected_code


def test_dont_bypass_validators_option_for_pydantic() -> None:
    code = CreateMappingMethodSourceCode(
        source_cls=PydanticV2ClassMeta(
            name="Source",
            fields={},
            use_construct=False,
            alias_name="Source",
        ),
        target_cls=PydanticV2ClassMeta(
            name="Target",
            fields={},
            use_construct=False,
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


def test_pydantic_alias() -> None:
    code = CreateMappingMethodSourceCode(
        source_cls=PydanticV2ClassMeta(
            name="Source",
            fields={},
            use_construct=False,
            alias_name="Source",
        ),
        target_cls=PydanticV2ClassMeta(
            name="Target",
            fields={},
            use_construct=False,
            alias_name="TargetAlias",
        ),
    )
    code.add_mapping(
        target=FieldMeta(name="target_x", type=int, allow_none=False, required=True, alias="TARGET_VARIABLE_X"),
        source=FieldMeta(name="source_x", type=int, allow_none=False, required=True),
    )
    expected_code = prepare_expected_code(
        """
        def convert(self, extra: dict) -> "Target":
            d = {}
            d["TARGET_VARIABLE_X"] = self.source_x
            return TargetAlias(**d)
        """
    )
    assert str(code) == expected_code


def test_pydantic_alias_allow_population_by_fields() -> None:
    code = CreateMappingMethodSourceCode(
        source_cls=PydanticV2ClassMeta(
            name="Source",
            fields={},
            use_construct=False,
            alias_name="Source",
        ),
        target_cls=PydanticV2ClassMeta(
            name="Target",
            fields={},
            use_construct=False,
            populate_by_name=True,
            alias_name="TargetAlias",
        ),
    )
    code.add_mapping(
        target=FieldMeta(name="target_x", type=int, allow_none=False, required=True, alias="TARGET_VARIABLE_X"),
        source=FieldMeta(name="source_x", type=int, allow_none=False, required=True),
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
