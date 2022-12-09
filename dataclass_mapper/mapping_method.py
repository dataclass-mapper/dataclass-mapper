from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from inspect import isfunction, signature
from typing import Any, Callable, Optional, Type, Union, cast, get_args, get_origin
from uuid import uuid4

from .classmeta import ClassMeta, DataclassType
from .fieldmeta import FieldMeta


class Spezial(Enum):
    USE_DEFAULT = auto()
    IGNORE_MISSING_MAPPING = auto()


# the different types that can be used as origin (source) for mapping to a member
# - str: the name of a different variable in the original class
# - Callable: a function that produces the value (can use `self` as parameter)
# - Other.USE_DEFAULT/IGNORE_MISSING_MAPPING: Don't map to this variable (only allowed if there is a default value/factory for it)
Origin = Union[str, Callable, Spezial]
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


class Assignment(ABC):
    def __init__(self, source: FieldMeta, target: FieldMeta):
        """
        :param source: meta infos about the source field
        :param target: meta infos about the target field
        """
        self.source = source
        self.target = target

    @abstractmethod
    def applicable(self) -> bool:
        ...

    @abstractmethod
    def right_side(self) -> str:
        ...


class SimpleAssignment(Assignment):
    def applicable(self) -> bool:
        return bool(self.target.type == self.source.type)

    def right_side(self) -> str:
        return get_var_name(self.source)


class RecursiveAssignment(Assignment):
    def applicable(self) -> bool:
        return is_mappable_to(self.source.type, self.target.type) and not (
            self.source.allow_none and self.target.disallow_none
        )

    def right_side(self) -> str:
        return self._get_map_func(get_var_name(self.source), target_cls=self.target.type)

    def _get_map_func(self, name: str, target_cls: Any) -> str:
        func_name = get_map_to_func_name(target_cls)
        return f"{name}.{func_name}()"


class ListRecursiveAssignment(RecursiveAssignment):
    def applicable(self) -> bool:
        return (
            get_origin(self.source.type) is list
            and get_origin(self.target.type) is list
            and is_mappable_to(get_args(self.source.type)[0], get_args(self.target.type)[0])
        )

    def right_side(self) -> str:
        list_item_type = get_args(self.target.type)[0]
        return f'[{self._get_map_func("x", target_cls=list_item_type)} for x in {get_var_name(self.source)}]'


class FunctionAssignment:
    def __init__(self, function: Callable, target: FieldMeta, methods: dict[str, Callable]):
        self.function = function
        self.target = target
        self.methods = methods

    def create_code(self) -> list[str]:
        name = f"_{uuid4().hex}"
        if len(signature(self.function).parameters) == 0:
            self.methods[name] = cast(Callable, staticmethod(self.function))
        else:
            # already a method
            # TODO assert that there is only one parameter and that it is `self`
            self.methods[name] = self.function
        return [f'    d["{self.target.name}"] = self.{name}()']


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

    def _add_line(self, left_side: str, right_side: str, indent=4) -> None:
        self.lines.append(f'{" "*indent}d["{left_side}"] = {right_side}')

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
        lines.append(f'{" "*indent}d["{target.name}"] = {right_side}')

        return lines

    def _get_options(self, source: FieldMeta, target: FieldMeta) -> AssignmentOptions:
        options = AssignmentOptions()

        # maintain Pydantic's unset property
        options.only_if_set = (
            source.allow_none
            and target.allow_none
            and not target.required
            and self.source_cls._type == self.target_cls._type == DataclassType.PYDANTIC
        )
        # TODO: what if the defaults of source/target are not just None?
        # How to map `x: Optional[int] = Field(42)` to `x: Optional[int] = Field(15)`?

        # handle optional to non-optional mappings
        if source.allow_none and target.disallow_none:
            if not target.required:
                options.only_if_not_None = True
            else:
                raise TypeError(
                    f"{source} of '{self.source_cls.name}' cannot be converted to {target}"
                )

        options.if_None = source.allow_none

        return options

    def add_mapping(self, target: FieldMeta, source: Union[FieldMeta, Callable]) -> None:
        if isfunction(source):
            function_assignment = FunctionAssignment(
                function=source, target=target, methods=self.methods
            )
            self.lines.extend(function_assignment.create_code())
        else:
            assert isinstance(source, FieldMeta)

            options = self._get_options(source=source, target=target)
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
        if self.target_cls._type == DataclassType.PYDANTIC and not self.target_cls.has_validators:
            return_statement = f"    return {self.target_cls.alias_name}.construct(**d)"
        else:
            return_statement = f"    return {self.target_cls.alias_name}(**d)"
        return "\n".join(self.lines + [return_statement])


def is_mappable_to(SourceCls: Any, TargetCls: Any) -> bool:
    func_name = get_map_to_func_name(TargetCls)
    return hasattr(SourceCls, func_name)


def get_map_to_func_name(cls: Any) -> str:
    return f"_map_to_{cls.__name__}"


def get_var_name(fieldmeta: FieldMeta) -> str:
    return f"self.{fieldmeta.name}"
