from dataclasses import dataclass
from textwrap import dedent
from dataclass_mapper.mapper import mapper

import pytest

from dataclass_mapper.fieldtypes import ClassFieldType, OptionalFieldType
from dataclass_mapper.implementations.base import FieldMeta
from dataclass_mapper.implementations.dataclasses import DataclassClassMeta
from dataclass_mapper.mapping_method import FromExtra, UpdateMappingMethodSourceCode


def prepare_expected_code(code: str) -> str:
    """remove empty lines and dedent"""
    return "\n".join(line for line in dedent(code).split("\n") if line)


@pytest.fixture
def code() -> UpdateMappingMethodSourceCode:
    return UpdateMappingMethodSourceCode(
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


def test_code_gen_add_normal_assignment(code: UpdateMappingMethodSourceCode) -> None:
    code.add_mapping(
        target=FieldMeta(name="target_x", type=ClassFieldType(int), required=True),
        source=FieldMeta(name="source_x", type=ClassFieldType(int), required=True),
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
        target=FieldMeta(name="target_x", type=ClassFieldType(int), required=False),
        source=FieldMeta(name="source_x", type=OptionalFieldType(ClassFieldType(int)), required=True),
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
        target=FieldMeta(name="target_x", type=ClassFieldType(FooTarget), required=True),
        source=FieldMeta(name="source_x", type=ClassFieldType(FooSource), required=True),
    )
    footarget_id = id(FooTarget)
    expected_code = prepare_expected_code(
        f"""
        def update(self, target: "Target", extra: dict) -> "None":
            target.target_x = self.source_x._map_to_FooTarget_{footarget_id}(extra)
        """  # noqa: E501
    )
    assert str(code) == expected_code


def test_provide_with_extra_code_check(code: UpdateMappingMethodSourceCode):
    code.add_from_extra(target=FieldMeta(name="target_x", type=ClassFieldType(int), required=True), source=FromExtra("external_x"))
    expected_code = prepare_expected_code(
        """
        def update(self, target: "Target", extra: dict) -> "None":
            if "external_x" not in extra:
                raise TypeError("When mapping an object of 'Source' to 'Target' the item 'external_x' needs to be provided in the `extra` dictionary")
            target.target_x = extra["external_x"]
        """  # noqa: E501
    )
    assert str(code) == expected_code
