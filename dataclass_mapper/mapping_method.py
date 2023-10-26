from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Dict, List, Optional, Type, Union

from . import code_generator as cg
from .assignments import (
    Assignment,
    CallableWithMax1Parameter,
    DictRecursiveAssignment,
    FunctionAssignment,
    ListRecursiveAssignment,
    RecursiveAssignment,
    SimpleAssignment,
    get_var_name,
)
from .implementations.base import ClassMeta, FieldMeta


class Spezial(Enum):
    USE_DEFAULT = auto()
    IGNORE_MISSING_MAPPING = auto()


@dataclass
class InitWithDefault:
    created_via: str


def init_with_default() -> InitWithDefault:
    """Initialize the target field with the default value, or default factory."""
    return InitWithDefault(created_via="init_with_default()")


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
class ProvideWithExtra:
    pass


def provide_with_extra() -> ProvideWithExtra:
    """Don't map this field using a source class field, fill it with a dictionary called `extra` duing `map_to`."""
    return ProvideWithExtra()


# the different types that can be used as origin (source) for mapping to a member
# - str: the name of a different variable in the original class
# - Callable: a function that produces the value (can use `self` as parameter)
# - Other.USE_DEFAULT/IGNORE_MISSING_MAPPING/init_with_default(): Don't map to this variable
#   (only allowed if there is a default value/factory for it)
# - assume_not_none(): assume that the source field is not None
# - provide_with_extra(): create no mapping between the classes, fill the field with a dictionary called `extra`
CurrentOrigin = Union[str, CallableWithMax1Parameter, InitWithDefault, AssumeNotNone, ProvideWithExtra]
Origin = Union[CurrentOrigin, Spezial]
CurrentStringFieldMapping = Dict[str, CurrentOrigin]
StringFieldMapping = Dict[str, Origin]


@dataclass
class AssignmentOptions:
    """
    Options for creating an assignment code (target = right_side).
    :param only_if_set: only set the target to the right_side if the source set
        (for Optional fields in Pydantic classes)
    :param only_if_not_None: don't assign the right side, if the value is None
        (for Optional -> non-Optional mappings with defaults in target fields)
    :param if_None: only assign the right side if it is not None (for Optional, recursive fields),
        otherwise set it to None
    """

    only_if_not_None: bool = False
    if_None: bool = False

    @classmethod
    def from_Metas(
        cls, source_cls: ClassMeta, target_cls: ClassMeta, source: FieldMeta, target: FieldMeta
    ) -> "AssignmentOptions":
        # handle optional to non-optional mappings
        only_if_not_None = False
        if source.allow_none and target.disallow_none:
            if not target.required:
                only_if_not_None = True
            else:
                raise TypeError(f"{source} of '{source_cls.name}' cannot be converted to {target}")

        if_None = source.allow_none

        return cls(
            only_if_not_None=only_if_not_None,
            if_None=if_None,
        )


class MappingMethodSourceCode(ABC):
    """Source code of the methods that are executed during mappings"""

    AssignmentClasses: List[Type[Assignment]] = [
        SimpleAssignment,
        RecursiveAssignment,
        ListRecursiveAssignment,
        DictRecursiveAssignment,
    ]

    def __init__(self, source_cls: ClassMeta, target_cls: ClassMeta) -> None:
        self.source_cls = source_cls
        self.target_cls = target_cls
        self.function = self._create_function(target_cls=target_cls)
        self.methods: Dict[str, Callable] = {}

    @staticmethod
    @abstractmethod
    def _create_function(target_cls: ClassMeta) -> cg.Function:
        pass

    @classmethod
    def _get_asssigment(cls, target: FieldMeta, source: FieldMeta) -> Optional[Assignment]:
        for AssignmentCls in cls.AssignmentClasses:
            if (assignment := AssignmentCls(source=source, target=target)).applicable():
                return assignment
        return None

    def _field_assignment(
        self,
        source: FieldMeta,
        target: FieldMeta,
        right_side: str,
        options: AssignmentOptions,
    ) -> cg.Statement:
        """Generate code for setting the target field to the right side.
        Only do it for a couple of conditions.

        :param right_side: some expression (code) that will be assigned to the target if conditions allow it
        """
        if options.if_None and not options.only_if_not_None:
            right_side = f"None if {get_var_name(source)} is None else {right_side}"
        code: cg.Statement = self._get_assignment(target, right_side)

        if options.only_if_not_None:
            code = cg.IfElse(condition=f"{get_var_name(source)} is not None", if_block=code)

        code = self.target_cls.post_process(code, source_cls=self.source_cls, source_field=source, target_field=target)
        return code

    @abstractmethod
    def _get_assignment(self, target: FieldMeta, right_side: str) -> cg.Assignment:
        pass

    def add_mapping(self, target: FieldMeta, source: Union[FieldMeta, Callable]) -> None:
        if callable(source):
            function_assignment = FunctionAssignment(
                function=source, target=target, methods=self.methods, target_cls_name=self.target_cls.name
            )
            right_side = function_assignment.right_side()
            self.function.body.append(self._get_assignment(target, right_side))
        else:
            assert isinstance(source, FieldMeta)

            options = AssignmentOptions.from_Metas(
                source_cls=self.source_cls, target_cls=self.target_cls, source=source, target=target
            )
            if assignment := self._get_asssigment(source=source, target=target):
                self.function.body.append(
                    self._field_assignment(
                        source=source,
                        target=target,
                        right_side=assignment.right_side(),
                        options=options,
                    )
                )
            else:  # impossible
                raise TypeError(f"{source} of '{self.source_cls.name}' cannot be converted to {target}")

    def add_fill_with_extra(self, target: FieldMeta) -> None:
        variable_name = self.target_cls.get_assignment_name(target)
        exception_msg = (
            f"When mapping an object of '{self.source_cls.name}' to '{self.target_cls.name}' "
            f"the field '{variable_name}' needs to be provided in the `extra` dictionary"
        )
        self.function.body.append(
            cg.IfElse(condition=f'"{variable_name}" not in extra', if_block=cg.Raise(f'TypeError("{exception_msg}")'))
        )
        self.function.body.append(self._get_assignment(target=target, right_side=f'extra["{variable_name}"]'))

    @abstractmethod
    def __str__(self) -> str:
        pass


class CreateMappingMethodSourceCode(MappingMethodSourceCode):
    """Source code of the method that is responsible for creating a new object"""

    @staticmethod
    def _create_function(target_cls: ClassMeta) -> cg.Function:
        return cg.Function(
            "convert",
            args="self, extra: dict",
            return_type=target_cls.name,
            body=cg.Block(cg.Assignment(name="d", rhs="{}")),
        )

    def _get_assignment(self, target: FieldMeta, right_side: str) -> cg.Assignment:
        variable_name = self.target_cls.get_assignment_name(target)
        lookup = cg.DictLookup(dict_name="d", key=variable_name)
        return cg.Assignment(name=lookup, rhs=right_side)

    def __str__(self) -> str:
        self.function.body.append(self.target_cls.return_statement())
        return self.function.to_string(0)


class UpdateMappingMethodSourceCode(MappingMethodSourceCode):
    """Source code of the method that is responsible for updating a new object"""

    @staticmethod
    def _create_function(target_cls: ClassMeta) -> cg.Function:
        return cg.Function(
            "update",
            args=f'self, target: "{target_cls.name}", extra: dict',
            return_type="None",
            body=cg.Block(),
        )

    def _get_assignment(self, target: FieldMeta, right_side: str) -> cg.Assignment:
        lookup = cg.AttributeLookup(obj="target", attribute=target.name)
        return cg.Assignment(name=lookup, rhs=right_side)

    def __str__(self) -> str:
        if not self.function.body:
            self.function.body.append(cg.Pass())
        return self.function.to_string(0)
