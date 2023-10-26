from dataclasses import dataclass
from textwrap import dedent
from typing import Dict, List

import pytest

from dataclass_mapper.implementations.base import FieldMeta
from dataclass_mapper.implementations.dataclasses import DataclassClassMeta
from dataclass_mapper.mapper import mapper
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


def test_code_gen_add_normal_assignment(code: CreateMappingMethodSourceCode) -> None:
    code.add_mapping(
        target=FieldMeta(name="target_x", type=int, allow_none=False, required=True),
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


def test_code_gen_add_assignment_only_if_not_None(code: CreateMappingMethodSourceCode) -> None:
    code.add_mapping(
        target=FieldMeta(name="target_x", type=int, allow_none=False, required=False),
        source=FieldMeta(name="source_x", type=int, allow_none=True, required=True),
    )
    expected_code = prepare_expected_code(
        """
        def convert(self, extra: dict) -> "Target":
            d = {}
            if self.source_x is not None:
                d["target_x"] = self.source_x
            return TargetAlias(**d)
        """
    )
    assert str(code) == expected_code


def test_bypass_validators_option_disabled_for_dataclasses() -> None:
    code = CreateMappingMethodSourceCode(
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
        def convert(self, extra: dict) -> "Target":
            d = {}
            return TargetAlias(**d)
        """
    )
    assert str(code) == expected_code


def test_provide_with_extra_code_check(code: CreateMappingMethodSourceCode):
    code.add_fill_with_extra(target=FieldMeta(name="target_x", type=int, allow_none=False, required=True))
    expected_code = prepare_expected_code(
        """
        def convert(self, extra: dict) -> "Target":
            d = {}
            if "target_x" not in extra:
                raise TypeError("When mapping an object of 'Source' to 'Target' the field 'target_x' needs to be provided in the `extra` dictionary")
            d["target_x"] = extra["target_x"]
            return TargetAlias(**d)
        """  # noqa: E501
    )
    assert str(code) == expected_code


def test_provide_with_extra_code_list(code: CreateMappingMethodSourceCode):
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
        def convert(self, extra: dict) -> "Target":
            d = {{}}
            d["target_x"] = [x._map_to_FooTarget_{footarget_id}(e) for x, e in self.__zip_longest(self.source_x, extra.get("target_x", []), fillvalue=dict())]
            return TargetAlias(**d)
        """  # noqa: E501
    )
    assert str(code) == expected_code


def test_provide_with_extra_code_dict(code: CreateMappingMethodSourceCode):
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
        def convert(self, extra: dict) -> "Target":
            d = {{}}
            d["target_x"] = {{k: v._map_to_FooTarget_{footarget_id}(extra.get("target_x", {{}}).get(k, {{}})) for k, v in self.source_x.items()}}
            return TargetAlias(**d)
        """  # noqa: E501
    )
    assert str(code) == expected_code
