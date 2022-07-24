from textwrap import dedent

import pytest

from dataclass_mapper.field import MetaField
from dataclass_mapper.mapping_method import MappingMethodSourceCode


def prepare_expected_code(code: str) -> str:
    """remove empty lines and dedent"""
    return "\n".join(line for line in dedent(code).split("\n") if line)


@pytest.fixture
def code() -> MappingMethodSourceCode:
    return MappingMethodSourceCode(
        source_cls_name="Source", target_cls_name="Target", target_cls_alias_name="TargetAlias"
    )


def test_code_gen_add_normal_assignment(code: MappingMethodSourceCode) -> None:
    code.add_assignment(
        target=MetaField(name="target_x", type=int, allow_none=False, required=True),
        source=MetaField(name="source_x", type=int, allow_none=False, required=True),
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
    code.add_assignment(
        target=MetaField(name="target_x", type=int, allow_none=False, required=False),
        source=MetaField(name="source_x", type=int, allow_none=True, required=True),
        only_if_not_None=True,
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
