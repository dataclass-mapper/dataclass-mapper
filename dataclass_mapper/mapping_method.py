import ast
from abc import ABC, abstractmethod
from dataclasses import replace
from inspect import signature
from typing import Callable, Dict, List, Optional
from uuid import uuid4

from dataclass_mapper.exceptions import ConvertingNotPossibleError, UpdatingNotPossibleError
from dataclass_mapper.expression_converters import map_expression
from dataclass_mapper.fieldtypes.not_supported import NotSupportedFieldType
from dataclass_mapper.mapper_mode import MapperMode
from dataclass_mapper.update_expressions import map_update_expression

from . import code_generator as cg
from .implementations.base import ClassMeta, FieldMeta
from .special_field_mappings import FromExtra

CTOR_DICT_VAR = cg.Variable("d")
SELF_VAR = cg.Variable("self")
EXTRA_VAR = cg.Variable("extra", cg.Constant("dict"))


class MappingMethodSourceCode(ABC):
    """Source code of the methods that are executed during mappings"""

    func_name = ""
    all_required_fields_need_initialization = True

    def __init__(self, source_cls: ClassMeta, target_cls: ClassMeta) -> None:
        self.source_cls = source_cls
        self.target_cls = target_cls
        self.attribute_assignments: List[cg.Statement] = []
        self.ctor_param_assignments: List[cg.Statement] = []
        self.factories: Dict[str, Callable] = {}

        self.TARGET_VAR = cg.Variable("target", cg.Constant(self.target_cls.name))

    @abstractmethod
    def _get_assignment(
        self, source: Optional[FieldMeta], target: FieldMeta, right_side: cg.Expression, only_if_source_is_set: bool
    ) -> cg.Statement:
        """Create the assignment code, either `d["x"] = right_side` or `target.x = right_side`
        depending if it's used for a ctor param or for a normal assignment.
        """

    @abstractmethod
    def _add(self, is_ctor_code: bool, statement: cg.Statement) -> None:
        """Add some statements, either ctor param assignment statements or assignment statements."""

    def _post_process(
        self, source: Optional[FieldMeta], target: FieldMeta, statement: cg.Statement, only_if_source_is_set: bool
    ) -> cg.Statement:
        # Don't skip, if the source was something special, like the extra dictionary or a factory.
        if source is None:
            return statement

        # Some classes (e.g. Pydantic) track if a field was set to None or was uninitialized.
        # By skipping the assignment, we can continue tracking the field over mappings.
        if skip_condition := self.source_cls.skip_condition(source_field=source, target_field=target):
            statement = cg.IfElse(skip_condition, [statement])

        # During updates it's possible to skip the assignment if the source field is None.
        if only_if_source_is_set:
            source_attribute = cg.AttributeLookup(obj=SELF_VAR, attribute=source.attribute_name)
            statement = cg.IfElse(source_attribute.is_not(cg.NONE), [statement])

        return statement

    @abstractmethod
    def add_mapping(self, target: FieldMeta, source: FieldMeta, only_if_source_is_set: bool = False) -> None:
        """Generate code for assigning the target field to the value of a source field.
        The value will be converted, if not already in the correct format.
        """

    @abstractmethod
    def get_ast(self) -> ast.Module:
        pass

    def add_factory(self, target: FieldMeta, source: Callable) -> None:
        """Generate code for a factory mapping.
        The field will be assigned to the result of the function/method call.
        """
        if (parameter_cnt := len(signature(source).parameters)) >= 2:
            # can only happen, if the typing annotation fails (e.g. because mypy is not installed)
            raise ValueError(
                f"'{target.attribute_name}' of '{self.target_cls.name}' cannot be mapped "
                "using a factory with more than one parameter"
            )

        factory_name = f"_{uuid4().hex}"
        self.factories[factory_name] = source

        factory = cg.DictLookup(cg.Variable("COLLECTION"), cg.Constant(factory_name))
        factory_call = cg.FunctionCall(factory, [] if parameter_cnt == 0 else [SELF_VAR])
        assignment = self._get_assignment(None, target, factory_call, only_if_source_is_set=False)
        self._add(target.init_with_ctor, assignment)

    def add_from_extra(self, target: FieldMeta, source: FromExtra) -> None:
        """Generate code for assign the result of a lookup in the extra dictionary to the field, if it exists.
        Raise an exception if it doesn't exist.
        """

        exception_msg = (
            f"When mapping an object of '{self.source_cls.name}' to '{self.target_cls.name}' "
            f"the item '{source.name}' needs to be provided in the `extra` dictionary"
        )

        key = cg.Constant(source.name)
        throw_exception_if_key_missing = cg.IfElse(
            condition=key.not_in_(EXTRA_VAR), if_block=[cg.Raise("TypeError", exception_msg)]
        )
        assignment_statement = self._get_assignment(
            source=None, target=target, right_side=cg.DictLookup(EXTRA_VAR, key), only_if_source_is_set=False
        )

        self._add(target.init_with_ctor, throw_exception_if_key_missing)
        self._add(target.init_with_ctor, assignment_statement)

    def _try_add_convert_statement(self, source: FieldMeta, target: FieldMeta, only_if_source_is_set: bool) -> bool:
        source_variable = cg.AttributeLookup(obj=SELF_VAR, attribute=source.attribute_name)
        try:
            convert_expression = map_expression(source.type, target.type, source_variable, 0)
        except ConvertingNotPossibleError:
            return False

        assignment = self._get_assignment(
            source, target, convert_expression, only_if_source_is_set=only_if_source_is_set
        )
        self._add(target.init_with_ctor, assignment)
        return True

    def _try_add_update_statement(self, source: FieldMeta, target: FieldMeta, only_if_source_is_set: bool) -> bool:
        source_attribute = cg.AttributeLookup(obj=SELF_VAR, attribute=source.attribute_name)
        target_attribute = cg.AttributeLookup(obj=self.TARGET_VAR, attribute=target.attribute_name)
        try:
            update_expression = map_update_expression(source.type, target.type, source_attribute, target_attribute, 0)
        except UpdatingNotPossibleError:
            return False

        update_statement = self._post_process(source, target, update_expression, only_if_source_is_set)
        self._add(target.init_with_ctor, update_statement)
        return True


class CreateMappingMethodSourceCode(MappingMethodSourceCode):
    """Source code of the method that is responsible for creating a new object.
    It first creates a new instance via the initializer, and afterwards fills all non-init fields.
    ```
    def convert(self, extra: "dict") -> "Target":
        d = {}
        d["ctor_param1"] = self.source1  # ctor_param_assignments
        d["ctor_param2"] = self.source2
        target = Target(**d)
        target.target3 = self.source3    # attribute_assignments
        target.target4 = self.source4
        return target
    ```
    """

    func_name = "convert"
    all_required_fields_need_initialization = True

    def _get_assignment(
        self, source: Optional[FieldMeta], target: FieldMeta, right_side: cg.Expression, only_if_source_is_set: bool
    ) -> cg.Statement:
        if target.init_with_ctor:
            dict_lookup = cg.DictLookup(dictionary=CTOR_DICT_VAR, key=cg.Constant(target.initializer_param_name))
            assignment = cg.Assignment(lhs=dict_lookup, rhs=right_side)
        else:
            lookup = cg.AttributeLookup(obj=self.TARGET_VAR, attribute=target.attribute_name)
            assignment = cg.Assignment(lhs=lookup, rhs=right_side)

        return self._post_process(source, target, assignment, only_if_source_is_set)

    def _add(self, is_ctor_code: bool, statement: cg.Statement) -> None:
        if is_ctor_code:
            self.ctor_param_assignments.append(statement)
        else:
            self.attribute_assignments.append(statement)

    def add_mapping(self, target: FieldMeta, source: FieldMeta, only_if_source_is_set: bool = False) -> None:
        """Generate code for assigning the target field to the value of a source field.
        The value will be converted, if not already in the correct format.
        """
        assert not only_if_source_is_set, "this parameter cannot be used for creation"

        if not self._try_add_convert_statement(
            source=source, target=target, only_if_source_is_set=only_if_source_is_set
        ):
            if isinstance(source.type, NotSupportedFieldType):
                raise TypeError(f"Field type '{source.type}' is not supported.")
            if isinstance(target.type, NotSupportedFieldType):
                raise TypeError(f"Field type '{target.type}' is not supported.")
            raise TypeError(
                f"{source} of '{self.source_cls.name}' cannot be converted to {target} of '{self.target_cls.name}'"
            ) from None

    def get_ast(self) -> ast.Module:
        function = cg.Function(
            self.func_name, args=[SELF_VAR, EXTRA_VAR], return_type=cg.Constant(self.target_cls.name), body=[]
        )

        # collect ctor parameters
        function.body.append(cg.Assignment(lhs=CTOR_DICT_VAR, rhs=cg.EmptyDict()))
        function.body.extend(self.ctor_param_assignments)

        # create object with ctor
        function.body.append(cg.Assignment(lhs=self.TARGET_VAR, rhs=self.target_cls.constructor_call()))

        # fill non-init attributes
        function.body.extend(self.attribute_assignments)

        # return object
        function.body.append(cg.Return(self.TARGET_VAR))

        return cg.Module([function]).generate_ast()


class UpdateMappingMethodSourceCode(MappingMethodSourceCode):
    """Source code of the method that is responsible for updating a new object.
    It will create an AST of a method that looks like the following.

    For an update method, it will look like:
    ```
    def update(self, target: "Target", extra: "dict") -> None:
        target.target1 = self.source1    # attribute_assignments
        target.target2 = self.source2
    ```
    """

    func_name = "update"
    all_required_fields_need_initialization = False

    def add_mapping(self, target: FieldMeta, source: FieldMeta, only_if_source_is_set: bool = False) -> None:
        # It doesn't matter anymore, if a field is required or not. The target field is already initialized.
        target = replace(target, required=False)

        if self._try_add_update_statement(source=source, target=target, only_if_source_is_set=only_if_source_is_set):
            return None
        if self._try_add_convert_statement(source=source, target=target, only_if_source_is_set=only_if_source_is_set):
            return None

        if isinstance(source.type, NotSupportedFieldType):
            raise TypeError(f"Field type '{source.type}' is not supported.")
        if isinstance(target.type, NotSupportedFieldType):
            raise TypeError(f"Field type '{target.type}' is not supported.")
        raise TypeError(
            f"{source} of '{self.source_cls.name}' cannot be converted "
            f"to {target} of '{self.target_cls.name}'. "
            f"The mapping is missing, or only exists for the {MapperMode.UPDATE} mode."
        )

    def _get_assignment(
        self, source: Optional[FieldMeta], target: FieldMeta, right_side: cg.Expression, only_if_source_is_set: bool
    ) -> cg.Statement:
        # Updates are always attribute assignements
        lookup = cg.AttributeLookup(obj=self.TARGET_VAR, attribute=target.attribute_name)
        assignment = cg.Assignment(lhs=lookup, rhs=right_side)
        return self._post_process(source, target, assignment, only_if_source_is_set)

    def _add(self, is_ctor_code: bool, statement: cg.Statement) -> None:
        # Updates are always attribute assignements
        self.attribute_assignments.append(statement)

    def get_ast(self) -> ast.Module:
        function = cg.Function(
            self.func_name,
            args=[SELF_VAR, self.TARGET_VAR, EXTRA_VAR],
            return_type=cg.Constant(None),
            body=self.attribute_assignments,
        )
        return cg.Module([function]).generate_ast()
