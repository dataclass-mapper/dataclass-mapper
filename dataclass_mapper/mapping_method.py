import ast
from abc import ABC, abstractmethod
from inspect import signature
from typing import Callable, Dict, cast
from uuid import uuid4

from dataclass_mapper.exceptions import ConvertingNotPossibleError, UpdatingNotPossibleError
from dataclass_mapper.expression_converters import map_expression
from dataclass_mapper.mapper_mode import MapperMode
from dataclass_mapper.update_expressions import map_update_expression

from . import code_generator as cg
from .implementations.base import ClassMeta, FieldMeta
from .special_field_mappings import FromExtra


class MappingMethodSourceCode(ABC):
    """Source code of the methods that are executed during mappings"""

    func_name = ""
    all_required_fields_need_initialization = True

    def __init__(self, source_cls: ClassMeta, target_cls: ClassMeta) -> None:
        self.source_cls = source_cls
        self.target_cls = target_cls
        self.function = self._create_function(source_cls=source_cls, target_cls=target_cls)
        self.methods: Dict[str, Callable] = {}

    @classmethod
    @abstractmethod
    def _create_function(cls, source_cls: ClassMeta, target_cls: ClassMeta) -> cg.Function:
        pass

    def _field_assignment(
        self,
        source: FieldMeta,
        target: FieldMeta,
        right_side: cg.Expression,
    ) -> cg.Statement:
        """Generate code for setting the target field to the right side.

        :param right_side: some expression (code) that will be assigned to the target if conditions allow it
        """
        code: cg.Statement = self._get_assignment(target, right_side)
        code = self.target_cls.post_process(code, source_cls=self.source_cls, source_field=source, target_field=target)
        return code

    @abstractmethod
    def _get_assignment(self, target: FieldMeta, right_side: cg.Expression) -> cg.Assignment:
        pass

    def add_callable(self, target: FieldMeta, source: Callable) -> None:
        if (parameter_cnt := len(signature(source).parameters)) >= 2:
            # can only happen, if the typing annotation fails (e.g. because mypy is not installed)
            raise ValueError(
                f"'{target.attribute_name}' of '{self.target_cls.name}' cannot be mapped "
                "using a factory with more than one parameter"
            )

        method_name = f"_{uuid4().hex}"
        if parameter_cnt == 0:
            self.methods[method_name] = cast(Callable, staticmethod(cast(Callable, source)))
        else:
            self.methods[method_name] = source

        right_side = cg.MethodCall(cg.Variable("self"), method_name, [])
        self.function.body.append(self._get_assignment(target, right_side))

    def add_mapping(self, target: FieldMeta, source: FieldMeta, only_if_source_is_set: bool = False) -> None:
        assert not only_if_source_is_set, "this parameter cannot be used for creation"

        source_variable = cg.AttributeLookup(obj=cg.Variable("self"), attribute=source.attribute_name)
        try:
            expression = map_expression(source.type, target.type, source_variable, 0)
        except ConvertingNotPossibleError:
            raise TypeError(
                f"{source} of '{self.source_cls.name}' cannot be converted to {target} of '{self.target_cls.name}'"
            )
        self.function.body.append(
            self._field_assignment(
                source=source,
                target=target,
                right_side=expression,
            )
        )

    def add_from_extra(self, target: FieldMeta, source: FromExtra) -> None:
        exception_msg = (
            f"When mapping an object of '{self.source_cls.name}' to '{self.target_cls.name}' "
            f"the item '{source.name}' needs to be provided in the `extra` dictionary"
        )

        extra = cg.Variable("extra")
        key = cg.Constant(source.name)
        self.function.body.append(
            cg.IfElse(condition=key.not_in_(extra), if_block=[cg.Raise("TypeError", exception_msg)])
        )
        self.function.body.append(self._get_assignment(target=target, right_side=cg.DictLookup(extra, key)))

    @abstractmethod
    def get_ast(self) -> ast.Module:
        pass


class CreateMappingMethodSourceCode(MappingMethodSourceCode):
    """Source code of the method that is responsible for creating a new object"""

    func_name = "convert"
    all_required_fields_need_initialization = True

    @classmethod
    def _create_function(cls, source_cls: ClassMeta, target_cls: ClassMeta) -> cg.Function:
        return cg.Function(
            cls.func_name,
            args=[cg.Arg("self"), cg.Arg("extra", cg.Constant("dict"))],
            return_type=cg.Constant(target_cls.name),
            body=[cg.Assignment(lhs=cg.Variable("d"), rhs=cg.EmptyDict())],
        )

    def _get_assignment(self, target: FieldMeta, right_side: cg.Expression) -> cg.Assignment:
        lookup = cg.DictLookup(dictionary=cg.Variable("d"), key=cg.Constant(target.initializer_param_name))
        return cg.Assignment(lhs=lookup, rhs=right_side)

    def get_ast(self) -> ast.Module:
        self.function.body.append(self.target_cls.return_statement())
        module = cg.Module([self.function])
        return module.generate_ast()


class UpdateMappingMethodSourceCode(MappingMethodSourceCode):
    """Source code of the method that is responsible for updating a new object"""

    func_name = "update"
    all_required_fields_need_initialization = False

    def add_mapping(self, target: FieldMeta, source: FieldMeta, only_if_source_is_set: bool = False) -> None:
        # It doesn't matter anymore, if a field is required or not. The target field is already initialized.
        target.required = False

        # overwrite method to handle recursive updates
        source_variable = cg.AttributeLookup(obj=cg.Variable("self"), attribute=source.attribute_name)
        target_variable = cg.AttributeLookup(obj=cg.Variable("target"), attribute=target.attribute_name)
        try:
            expression = map_update_expression(source.type, target.type, source_variable, target_variable, 0)
            code: cg.Statement = cg.ExpressionStatement(expression)
            code = self.target_cls.post_process(
                code, source_cls=self.source_cls, source_field=source, target_field=target
            )
        except UpdatingNotPossibleError:
            try:
                expression = map_expression(source.type, target.type, source_variable, 0)
            except ConvertingNotPossibleError:
                raise TypeError(
                    f"{source} of '{self.source_cls.name}' cannot be converted "
                    f"to {target} of '{self.target_cls.name}'. "
                    f"The mapping is missing, or only exists for the {MapperMode.UPDATE} mode."
                )
            code = self._field_assignment(
                source=source,
                target=target,
                right_side=expression,
            )

        if only_if_source_is_set:
            code = cg.IfElse(source_variable.is_not(cg.NONE), [code])
        self.function.body.append(code)

    @classmethod
    def _create_function(cls, source_cls: ClassMeta, target_cls: ClassMeta) -> cg.Function:
        return cg.Function(
            cls.func_name,
            args=[cg.Arg("self"), cg.Arg("target", cg.Constant(target_cls.name)), cg.Arg("extra", cg.Constant("dict"))],
            return_type=cg.Constant(None),
            body=[],
        )

    def _get_assignment(self, target: FieldMeta, right_side: cg.Expression) -> cg.Assignment:
        lookup = cg.AttributeLookup(obj=cg.Variable("target"), attribute=target.attribute_name)
        return cg.Assignment(lhs=lookup, rhs=right_side)

    def get_ast(self) -> ast.Module:
        return cg.Module([self.function]).generate_ast()
