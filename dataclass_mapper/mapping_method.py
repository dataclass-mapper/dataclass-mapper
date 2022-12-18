from dataclasses import dataclass
from enum import Enum, auto
from inspect import isfunction
from typing import Callable, Optional, Type, Union

from .assignments import (
    Assignment,
    FunctionAssignment,
    ListRecursiveAssignment,
    RecursiveAssignment,
    SimpleAssignment,
    get_var_name,
)
from .classmeta import ClassMeta, DataclassType
from .fieldmeta import FieldMeta


class Spezial(Enum):
    USE_DEFAULT = auto()
    IGNORE_MISSING_MAPPING = auto()


@dataclass
class InitWithDefault:
    pass


def init_with_default() -> InitWithDefault:
    """Initialize the target field with the default value, or default factory."""
    return InitWithDefault()


@dataclass
class AssumeNotNone:
    field_name: Optional[str] = None


def assume_not_none(field_name: Optional[str] = None) -> AssumeNotNone:
    """Assume that the source field is not none, even if it is an optional field.
    Allows a mapping from Optional[T] to T."""
    return AssumeNotNone(field_name)


# the different types that can be used as origin (source) for mapping to a member
# - str: the name of a different variable in the original class
# - Callable: a function that produces the value (can use `self` as parameter)
# - Other.USE_DEFAULT/IGNORE_MISSING_MAPPING/init_with_default(): Don't map to this variable (only allowed if there is a default value/factory for it)
# - assume_not_none(): assume that the source field is not None
Origin = Union[str, Callable, Spezial, InitWithDefault, AssumeNotNone]
StringFieldMapping = dict[str, Origin]


@dataclass
class AssignmentOptions:
    """
    Options for creating an assignment code (target = right_side).
    :param only_if_set: only set the target to the right_side if the source set (for Optional fields in Pydantic classes)
    :param only_if_not_None: don't assign the right side, if the value is None (for Optional -> non-Optional mappings with defaults in target fields)
    :param if_None: only assign the right side if it is not None (for Optional, recursive fields), otherwise set it to None
    """

    only_if_set: bool = False
    only_if_not_None: bool = False
    if_None: bool = False

    @classmethod
    def from_Metas(
        cls, source_cls: ClassMeta, target_cls: ClassMeta, source: FieldMeta, target: FieldMeta
    ) -> "AssignmentOptions":
        # maintain Pydantic's unset property
        only_if_set = (
            source.allow_none
            and target.allow_none
            and not target.required
            and source_cls._type == target_cls._type == DataclassType.PYDANTIC
        )
        # TODO: what if the defaults of source/target are not just None?
        # How to map `x: Optional[int] = Field(42)` to `x: Optional[int] = Field(15)`?

        # handle optional to non-optional mappings
        only_if_not_None = False
        if source.allow_none and target.disallow_none:
            if not target.required:
                only_if_not_None = True
            else:
                raise TypeError(f"{source} of '{source_cls.name}' cannot be converted to {target}")

        if_None = source.allow_none

        return cls(
            only_if_set=only_if_set,
            only_if_not_None=only_if_not_None,
            if_None=if_None,
        )


class MappingMethodSourceCode:
    """Source code of the mapping method"""

    AssignmentClasses: list[Type[Assignment]] = [
        SimpleAssignment,
        RecursiveAssignment,
        ListRecursiveAssignment,
    ]

    def __init__(self, source_cls: ClassMeta, target_cls: ClassMeta) -> None:
        self.source_cls = source_cls
        self.target_cls = target_cls
        self.lines = [
            f'def convert(self) -> "{self.target_cls.name}":',
            f"    d = {{}}",
        ]
        self.methods: dict[str, Callable] = {}

    @classmethod
    def _get_asssigment(cls, target: FieldMeta, source: FieldMeta) -> Optional[Assignment]:
        for AssignmentCls in cls.AssignmentClasses:
            if (assignment := AssignmentCls(source=source, target=target)).applicable():
                return assignment
        return None

    def _assignment_lines(
        self,
        source: FieldMeta,
        target: FieldMeta,
        right_side: str,
        options: AssignmentOptions,
    ) -> list[str]:
        """Generate code for setting the target field to the right side.
        Only do it for a couple of conditions.

        :param right_side: some expression (code) that will be assigned to the target if conditions allow it
        """
        lines: list[str] = []
        indent = 4
        if options.only_if_not_None:
            lines.append(f"    if {get_var_name(source)} is not None:")
            indent = 8
        if options.only_if_set:
            lines.append(f"    if '{source.name}' in self.__fields_set__:")
            indent = 8

        right_side = right_side
        if options.if_None and not options.only_if_not_None:
            right_side = f"None if {get_var_name(source)} is None else {right_side}"
        lines.append(self._get_assignment_str(target, right_side, indent))
        return lines

    def _get_assignment_str(self, target: FieldMeta, right_side: str, indent: int = 4) -> str:
        variable_name = self.target_cls.get_assignment_name(target)
        return f'{" "*indent}d["{variable_name}"] = {right_side}'

    def add_mapping(self, target: FieldMeta, source: Union[FieldMeta, Callable]) -> None:
        if isfunction(source):
            function_assignment = FunctionAssignment(
                function=source, target=target, methods=self.methods
            )
            right_side = function_assignment.right_side()
            self.lines.append(self._get_assignment_str(target, right_side))
        else:
            assert isinstance(source, FieldMeta)

            options = AssignmentOptions.from_Metas(
                source_cls=self.source_cls, target_cls=self.target_cls, source=source, target=target
            )
            if assignment := self._get_asssigment(source=source, target=target):
                self.lines.extend(
                    self._assignment_lines(
                        source=source,
                        target=target,
                        right_side=assignment.right_side(),
                        options=options,
                    )
                )
            else:  # impossible
                raise TypeError(
                    f"{source} of '{self.source_cls.name}' cannot be converted to {target}"
                )

    def __str__(self) -> str:
        return "\n".join(self.lines + [self.target_cls.return_statement()])
