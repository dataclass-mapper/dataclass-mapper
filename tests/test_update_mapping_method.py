from dataclasses import dataclass
from textwrap import dedent

import pytest

from dataclass_mapper.fieldtypes import ClassFieldType
from dataclass_mapper.implementations.base import FieldMeta
from dataclass_mapper.implementations.dataclasses import DataclassClassMeta
from dataclass_mapper.mapper import mapper
from dataclass_mapper.mapping_method import FromExtra, UpdateMappingMethodSourceCode
from tests.utils import assert_ast_equal


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
            internal_name="Source",
        ),
        target_cls=DataclassClassMeta(
            name="Target",
            fields={},
            clazz=None,
            internal_name="TargetAlias",
        ),
    )


def test_code_gen_add_normal_assignment(code: UpdateMappingMethodSourceCode) -> None:
    code.add_mapping(
        target=FieldMeta(
            attribute_name="target_x",
            type=ClassFieldType(int),
            required=True,
            initializer_param_name="target_x",
            init_with_ctor=True,
        ),
        source=FieldMeta(
            attribute_name="source_x",
            type=ClassFieldType(int),
            required=True,
            initializer_param_name="source_x",
            init_with_ctor=True,
        ),
    )
    expected_code = prepare_expected_code(
        """
        def update(self, target: "Target", extra: "dict") -> None:
            target.target_x = self.source_x
        """
    )
    assert_ast_equal(code.get_ast(), expected_code)


def test_code_gen_alias_not_used_for_update(code: UpdateMappingMethodSourceCode) -> None:
    code.add_mapping(
        target=FieldMeta(
            attribute_name="target_x",
            type=ClassFieldType(int),
            required=True,
            initializer_param_name="TARGET_X",
            init_with_ctor=True,
        ),
        source=FieldMeta(
            attribute_name="source_x",
            type=ClassFieldType(int),
            required=True,
            initializer_param_name="source_x",
            init_with_ctor=True,
        ),
    )
    expected_code = prepare_expected_code(
        """
        def update(self, target: "Target", extra: "dict") -> None:
            target.target_x = self.source_x
        """
    )
    assert_ast_equal(code.get_ast(), expected_code)


def test_code_gen_add_assignment_only_if_not_None(code: UpdateMappingMethodSourceCode) -> None:
    code.add_mapping(
        target=FieldMeta(
            attribute_name="target_x",
            type=ClassFieldType(int),
            required=False,
            initializer_param_name="target_x",
            init_with_ctor=True,
        ),
        source=FieldMeta(
            attribute_name="source_x",
            type=ClassFieldType(int),
            required=True,
            initializer_param_name="source_x",
            init_with_ctor=True,
        ),
        only_if_source_is_set=True,
    )
    expected_code = prepare_expected_code(
        """
        def update(self, target: "Target", extra: "dict") -> None:
            if self.source_x is not None:
                target.target_x = self.source_x
        """
    )
    assert_ast_equal(code.get_ast(), expected_code)


def test_bypass_validators_option_disabled_for_dataclasses() -> None:
    code = UpdateMappingMethodSourceCode(
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
        def update(self, target: "Target", extra: "dict") -> None:
            pass
        """
    )
    assert_ast_equal(code.get_ast(), expected_code)


def test_recursive_update(code: UpdateMappingMethodSourceCode):
    @dataclass
    class FooTarget:
        pass

    @mapper(FooTarget)
    @dataclass
    class FooSource:
        pass

    code.add_mapping(
        target=FieldMeta(
            attribute_name="target_x",
            type=ClassFieldType(FooTarget),
            required=True,
            initializer_param_name="target_x",
            init_with_ctor=True,
        ),
        source=FieldMeta(
            attribute_name="source_x",
            type=ClassFieldType(FooSource),
            required=True,
            initializer_param_name="source_x",
            init_with_ctor=True,
        ),
    )
    footarget_id = id(FooTarget)
    expected_code = prepare_expected_code(
        f"""
        def update(self, target: "Target", extra: "dict") -> None:
            self.source_x._mapupdate_to_FooTarget_{footarget_id}(target.target_x, extra)
        """
    )
    assert_ast_equal(code.get_ast(), expected_code)


def test_provide_with_extra_code_check(code: UpdateMappingMethodSourceCode):
    code.add_from_extra(
        target=FieldMeta(
            attribute_name="target_x",
            type=ClassFieldType(int),
            required=True,
            initializer_param_name="target_x",
            init_with_ctor=True,
        ),
        source=FromExtra("external_x"),
    )
    expected_code = prepare_expected_code(
        """
        def update(self, target: "Target", extra: "dict") -> None:
            if "external_x" not in extra:
                raise TypeError("When mapping an object of 'Source' to 'Target' the item 'external_x' needs to be provided in the `extra` dictionary")
            target.target_x = extra["external_x"]
        """  # noqa: E501
    )
    assert_ast_equal(code.get_ast(), expected_code)
