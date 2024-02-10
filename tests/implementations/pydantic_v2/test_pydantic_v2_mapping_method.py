from textwrap import dedent

import pytest

from dataclass_mapper.implementations.dataclasses import DataclassClassMeta
from dataclass_mapper.implementations.pydantic_v2 import PydanticV2ClassMeta
from dataclass_mapper.mapping_method import CreateMappingMethodSourceCode
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


def test_bypass_validators_option_for_pydantic() -> None:
    code = CreateMappingMethodSourceCode(
        source_cls=PydanticV2ClassMeta(
            name="Source",
            fields={},
            clazz=None,
            use_construct=False,
            internal_name="Source",
        ),
        target_cls=PydanticV2ClassMeta(
            name="Target",
            fields={},
            clazz=None,
            use_construct=True,
            internal_name="TargetAlias",
        ),
    )
    expected_code = prepare_expected_code(
        """
        def convert(self, extra: "dict") -> "Target":
            d = {}
            target = TargetAlias.model_construct(**d)
            return target
        """
    )
    assert_ast_equal(code.get_ast(), expected_code)


def test_dont_bypass_validators_option_for_pydantic() -> None:
    code = CreateMappingMethodSourceCode(
        source_cls=PydanticV2ClassMeta(
            name="Source",
            fields={},
            clazz=None,
            use_construct=False,
            internal_name="Source",
        ),
        target_cls=PydanticV2ClassMeta(
            name="Target",
            fields={},
            clazz=None,
            use_construct=False,
            internal_name="TargetAlias",
        ),
    )
    expected_code = prepare_expected_code(
        """
        def convert(self, extra: "dict") -> "Target":
            d = {}
            target = TargetAlias(**d)
            return target
        """
    )
    assert_ast_equal(code.get_ast(), expected_code)
