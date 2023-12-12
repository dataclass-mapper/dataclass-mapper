from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum, auto
from inspect import signature
from typing import Any, Callable, Dict, Optional, Union, cast
from uuid import uuid4

from dataclass_mapper.exceptions import ConvertingNotPossibleError, UpdatingNotPossibleError
from dataclass_mapper.expression_converters import map_expression
from dataclass_mapper.fieldtypes.optional import OptionalFieldType
from dataclass_mapper.implementations.sqlalchemy import InstrumentedAttribute
from dataclass_mapper.mapper_mode import MapperMode
from dataclass_mapper.update_expressions import update_expression

from . import code_generator as cg
from .implementations.base import ClassMeta, FieldMeta


class Spezial(Enum):
    USE_DEFAULT = auto()
    IGNORE_MISSING_MAPPING = auto()


@dataclass
class Ignore:
    created_via: str


def init_with_default() -> Ignore:
    """Initialize the target field with the default value, or default factory."""
    return Ignore(created_via="init_with_default()")


def ignore() -> Ignore:
    """If the mapping operation creates a new object, it will initialize the target field
    with the default value, or default factory.
    If the mapping operation updates a field, it will simply ignore that field and keep the
    old value.
    """
    return Ignore(created_via="ignore()")


@dataclass
class AssumeNotNone:
    field_name: Optional[str] = None


def assume_not_none(field_name: Optional[str] = None) -> AssumeNotNone:
    """Assume that the source field is not none, even if it is an optional field.
    Allows a mapping from ``Optional[T]`` to ``T``.
    If the field name is not specified, it is assumed that the source field has the same name as the target field.
    """
    return AssumeNotNone(field_name)


@dataclass
class FromExtra:
    name: str


def from_extra(name: str) -> FromExtra:
    """Don't map this field using a source class field, fill it with a dictionary called `extra` duing `map_to`."""
    return FromExtra(name)


CallableWithMax1Parameter = Union[Callable[[], Any], Callable[[Any], Any]]


# the different types that can be used as origin (source) for mapping to a member
# - str: the name of a different variable in the original class
# - Callable: a function that produces the value (can use `self` as parameter)
# - Other.USE_DEFAULT/IGNORE_MISSING_MAPPING/init_with_default()/ignore(): Don't map to this variable
#   (only allowed if there is a default value/factory for it)
# - assume_not_none(): assume that the source field is not None
# - from_extra(): create no mapping between the classes, fill the field with a dictionary called `extra`
CurrentOrigin = Union[str, CallableWithMax1Parameter, Ignore, AssumeNotNone, FromExtra]
Origin = Union[CurrentOrigin, Spezial]
CurrentStringFieldMapping = Dict[str, CurrentOrigin]
StringFieldMapping = Dict[str, Origin]
StringSqlAlchemyFieldMapping = Dict[Union[str, InstrumentedAttribute], Union[Origin, InstrumentedAttribute]]


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
                f"'{target.name}' of '{self.target_cls.name}' cannot be mapped "
                "using a factory with more than one parameter"
            )

        method_name = f"_{uuid4().hex}"
        if parameter_cnt == 0:
            self.methods[method_name] = cast(Callable, staticmethod(cast(Callable, source)))
        else:
            self.methods[method_name] = source

        right_side = cg.MethodCall(cg.Variable("self"), method_name, [])
        self.function.body.append(self._get_assignment(target, right_side))

    def add_mapping(self, target: FieldMeta, source: FieldMeta) -> None:
        source_variable = cg.AttributeLookup(obj="self", attribute=source.name)
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
        key = cg.StringValue(source.name)
        self.function.body.append(
            cg.IfElse(condition=key.not_in_(extra), if_block=cg.Raise(f'TypeError("{exception_msg}")'))
        )
        self.function.body.append(self._get_assignment(target=target, right_side=cg.DictLookup(extra, key)))

    @abstractmethod
    def __str__(self) -> str:
        pass


class CreateMappingMethodSourceCode(MappingMethodSourceCode):
    """Source code of the method that is responsible for creating a new object"""

    func_name = "convert"
    all_required_fields_need_initialization = True

    @classmethod
    def _create_function(cls, source_cls: ClassMeta, target_cls: ClassMeta) -> cg.Function:
        return cg.Function(
            cls.func_name,
            args="self, extra: dict",
            return_type=target_cls.name,
            body=cg.Block(cg.Assignment(name="d", rhs="{}")),
        )

    def _get_assignment(self, target: FieldMeta, right_side: cg.Expression) -> cg.Assignment:
        variable_name = self.target_cls.get_assignment_name(target)
        lookup = cg.DictLookup(dict_name="d", key=variable_name)
        return cg.Assignment(name=lookup, rhs=right_side)

    def __str__(self) -> str:
        self.function.body.append(self.target_cls.return_statement())
        return self.function.to_string(0)


class UpdateMappingMethodSourceCode(MappingMethodSourceCode):
    """Source code of the method that is responsible for updating a new object"""

    func_name = "update"
    all_required_fields_need_initialization = False

    def add_mapping(self, target: FieldMeta, source: FieldMeta) -> None:
        # It doesn't matter anymore, if a field is required or not. The target field is already initialized.
        target.required = False

        # overwrite method to handle recursive updates
        source_variable = cg.AttributeLookup(obj="self", attribute=source.name)
        target_variable = cg.AttributeLookup(obj="target", attribute=target.name)
        try:
            expression = update_expression(source.type, target.type, source_variable, target_variable, 0)
            code = cg.ExpressionStatement(expression)
            code = self.target_cls.post_process(code, source_cls=self.source_cls, source_field=source, target_field=target)
            self.function.body.append(code)
        except UpdatingNotPossibleError:
            # raise TypeError(
            #     f"{source} of '{self.source_cls.name}' cannot be updated to {target} of '{self.target_cls.name}'"
            #     # TODO: fix bad grammar
            # )

            try:
                expression = map_expression(source.type, target.type, source_variable, 0)
            except ConvertingNotPossibleError:
                raise TypeError(
                    f"{source} of '{self.source_cls.name}' cannot be converted to {target} of '{self.target_cls.name}'. The mapping is missing, or only exists for the {MapperMode.UPDATE} mode."
                )
            self.function.body.append(
                self._field_assignment(
                    source=source,
                    target=target,
                    right_side=expression,
                )
            )

    @classmethod
    def _create_function(cls, source_cls: ClassMeta, target_cls: ClassMeta) -> cg.Function:
        return cg.Function(
            cls.func_name,
            args=f'self, target: "{target_cls.name}", extra: dict',
            return_type="None",
            body=cg.Block(),
        )

    def _get_assignment(self, target: FieldMeta, right_side: cg.Expression) -> cg.Assignment:
        lookup = cg.AttributeLookup(obj="target", attribute=target.name)
        return cg.Assignment(name=lookup, rhs=right_side)

    def __str__(self) -> str:
        if not self.function.body:
            self.function.body.append(cg.Pass())
        return self.function.to_string(0)
