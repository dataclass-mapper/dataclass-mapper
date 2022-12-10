from textwrap import dedent

import pytest

from dataclass_mapper.classmeta import DataclassClassMeta, FieldMeta, PydanticClassMeta
from dataclass_mapper.mapping_method import MappingMethodSourceCode


def prepare_expected_code(code: str) -> str:
    """remove empty lines and dedent"""
    return "\n".join(line for line in dedent(code).split("\n") if line)


@pytest.fixture
def code() -> MappingMethodSourceCode:
    return MappingMethodSourceCode(
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


def test_code_gen_add_normal_assignment(code: MappingMethodSourceCode) -> None:
    code.add_mapping(
        target=FieldMeta(name="target_x", type=int, allow_none=False, required=True),
        source=FieldMeta(name="source_x", type=int, allow_none=False, required=True),
    )
    expected_code = prepare_expected_code(
        """
        def convert(self) -> "Target":
            d = {}
            d["target_x"] = self.source_x
            return TargetAlias(**d)
        """
    )
    assert str(code) == expected_code


def test_code_gen_add_assignment_only_if_not_None(code: MappingMethodSourceCode) -> None:
    code.add_mapping(
        target=FieldMeta(name="target_x", type=int, allow_none=False, required=False),
        source=FieldMeta(name="source_x", type=int, allow_none=True, required=True),
    )
    expected_code = prepare_expected_code(
        """
        def convert(self) -> "Target":
            d = {}
            if self.source_x is not None:
                d["target_x"] = self.source_x
            return TargetAlias(**d)
        """
    )
    assert str(code) == expected_code


def test_bypass_validators_option_for_pydantic() -> None:
    code = MappingMethodSourceCode(
        source_cls=PydanticClassMeta(
            name="Source",
            fields={},
            use_construct=False,
            alias_name="Source",
        ),
        target_cls=PydanticClassMeta(
            name="Target",
            fields={},
            use_construct=True,
            alias_name="TargetAlias",
        ),
    )
    expected_code = prepare_expected_code(
        """
        def convert(self) -> "Target":
            d = {}
            return TargetAlias.construct(**d)
        """
    )
    assert str(code) == expected_code


def test_dont_bypass_validators_option_for_pydantic() -> None:
    code = MappingMethodSourceCode(
        source_cls=PydanticClassMeta(
            name="Source",
            fields={},
            use_construct=False,
            alias_name="Source",
        ),
        target_cls=PydanticClassMeta(
            name="Target",
            fields={},
            use_construct=False,
            alias_name="TargetAlias",
        ),
    )
    expected_code = prepare_expected_code(
        """
        def convert(self) -> "Target":
            d = {}
            return TargetAlias(**d)
        """
    )
    assert str(code) == expected_code


def test_bypass_validators_option_disabled_for_dataclasses() -> None:
    code = MappingMethodSourceCode(
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
    expected_code = prepare_expected_code(
        """
        def convert(self) -> "Target":
            d = {}
            return TargetAlias(**d)
        """
    )
    assert str(code) == expected_code
