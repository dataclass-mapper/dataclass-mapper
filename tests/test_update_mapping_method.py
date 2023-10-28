from dataclasses import dataclass
from textwrap import dedent
from typing import Dict, List

import pytest

from dataclass_mapper.implementations.base import FieldMeta
from dataclass_mapper.implementations.dataclasses import DataclassClassMeta
from dataclass_mapper.mapper import mapper
from dataclass_mapper.mapping_method import UpdateMappingMethodSourceCode


def prepare_expected_code(code: str) -> str:
    """remove empty lines and dedent"""
    return "\n".join(line for line in dedent(code).split("\n") if line)


@pytest.fixture
def code() -> UpdateMappingMethodSourceCode:
    return UpdateMappingMethodSourceCode(
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


def test_code_gen_add_normal_assignment(code: UpdateMappingMethodSourceCode) -> None:
    code.add_mapping(
        target=FieldMeta(name="target_x", type=int, allow_none=False, required=True),
        source=FieldMeta(name="source_x", type=int, allow_none=False, required=True),
    )
    expected_code = prepare_expected_code(
        """
        def update(self, target: "Target", extra: dict) -> "None":
            target.target_x = self.source_x
        """
    )
    assert str(code) == expected_code


def test_code_gen_add_assignment_only_if_not_None(code: UpdateMappingMethodSourceCode) -> None:
    code.add_mapping(
        target=FieldMeta(name="target_x", type=int, allow_none=False, required=False),
        source=FieldMeta(name="source_x", type=int, allow_none=True, required=True),
    )
    expected_code = prepare_expected_code(
        """
        def update(self, target: "Target", extra: dict) -> "None":
            if self.source_x is not None:
                target.target_x = self.source_x
        """
    )
    assert str(code) == expected_code


def test_bypass_validators_option_disabled_for_dataclasses() -> None:
    code = UpdateMappingMethodSourceCode(
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
        def update(self, target: "Target", extra: dict) -> "None":
            pass
        """
    )
    assert str(code) == expected_code


def test_provide_with_extra_code_list_update(code: UpdateMappingMethodSourceCode):
    @dataclass
    class FooTarget:
        pass

    @mapper(FooTarget)
    @dataclass
    class FooSource:
        pass

    code.add_mapping(
        target=FieldMeta(name="target_x", type=FooTarget, allow_none=False, required=True),
        source=FieldMeta(name="source_x", type=FooSource, allow_none=False, required=True),
    )
    footarget_id = id(FooTarget)
    expected_code = prepare_expected_code(
        f"""
        def update(self, target: "Target", extra: dict) -> "None":
            target.target_x = self.source_x._map_to_FooTarget_{footarget_id}(extra.get("target_x", {{}}))
        """  # noqa: E501
    )
    assert str(code) == expected_code


def test_provide_with_extra_code_check(code: UpdateMappingMethodSourceCode):
    code.add_fill_with_extra(target=FieldMeta(name="target_x", type=int, allow_none=False, required=True))
    expected_code = prepare_expected_code(
        """
        def update(self, target: "Target", extra: dict) -> "None":
            if "target_x" not in extra:
                raise TypeError("When mapping an object of 'Source' to 'Target' the field 'target_x' needs to be provided in the `extra` dictionary")
            target.target_x = extra["target_x"]
        """  # noqa: E501
    )
    assert str(code) == expected_code


def test_provide_with_extra_code_list(code: UpdateMappingMethodSourceCode):
    @dataclass
    class FooTarget:
        pass

    @mapper(FooTarget)
    @dataclass
    class FooSource:
        pass

    code.add_mapping(
        target=FieldMeta(name="target_x", type=List[FooTarget], allow_none=False, required=True),
        source=FieldMeta(name="source_x", type=List[FooSource], allow_none=False, required=True),
    )
    footarget_id = id(FooTarget)
    expected_code = prepare_expected_code(
        f"""
        def update(self, target: "Target", extra: dict) -> "None":
            target.target_x = [x._map_to_FooTarget_{footarget_id}(e) for x, e in self.__zip_longest(self.source_x, extra.get("target_x", []), fillvalue=dict())]
        """  # noqa: E501
    )
    assert str(code) == expected_code


def test_provide_with_extra_code_dict(code: UpdateMappingMethodSourceCode):
    @dataclass
    class FooTarget:
        pass

    @mapper(FooTarget)
    @dataclass
    class FooSource:
        pass

    code.add_mapping(
        target=FieldMeta(name="target_x", type=Dict[str, FooTarget], allow_none=False, required=True),
        source=FieldMeta(name="source_x", type=Dict[str, FooSource], allow_none=False, required=True),
    )
    footarget_id = id(FooTarget)
    expected_code = prepare_expected_code(
        f"""
        def update(self, target: "Target", extra: dict) -> "None":
            target.target_x = {{k: v._map_to_FooTarget_{footarget_id}(extra.get("target_x", {{}}).get(k, {{}})) for k, v in self.source_x.items()}}
        """  # noqa: E501
    )
    assert str(code) == expected_code
