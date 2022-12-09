from dataclasses import dataclass
from enum import Enum, auto
from inspect import isfunction, signature
from typing import Any, Callable, Union, cast, get_args, get_origin, Optional, Type
from uuid import uuid4
from abc import ABC, abstractmethod

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
    def right_side(self) -> str:
        ...

    def create_code(
        self,
        options: AssignmentOptions,
    ) -> list[str]:
        """Generate code for setting the target field to the right side.
        Only do it for a couple of conditions.

        :param right_side: some expression (code) that will be assigned to the target if conditions allow it
        """
        lines: list[str] = []
        indent = 4
        if options.only_if_not_None:
            lines.append(f"    if {get_var_name(self.source)} is not None:")
            indent = 8
        if options.only_if_set:
            lines.append(f"    if '{self.source.name}' in self.__fields_set__:")
            indent = 8

        right_side = self.right_side()
        if options.if_None:
            right_side = f"None if {get_var_name(self.source)} is None else {right_side}"
        lines.append(f'{" "*indent}d["{self.target.name}"] = {right_side}')

        return lines


class SimpleAssignment(Assignment):
    def right_side(self) -> str:
        return get_var_name(self.source)

class RecursiveAssignment(Assignment):
    def right_side(self) -> str:
        return self._get_map_func(get_var_name(self.source), target_cls=self.target.type)

    def _get_map_func(self, name: str, target_cls: Any) -> str:
        func_name = get_map_to_func_name(target_cls)
        return f"{name}.{func_name}()"

class ListRecursiveAssignment(RecursiveAssignment):
    def right_side(self) -> str:
        list_item_type = get_args(self.target.type)[0]
        return f'[{self._get_map_func("x", target_cls=list_item_type)} for x in {get_var_name(self.source)}]'


class MappingMethodSourceCode:
    """Source code of the mapping method"""

    def __init__(
        self, source_cls: ClassMeta, target_cls: ClassMeta
    ) -> None:
        self.source_cls = source_cls
        self.target_cls = target_cls
        self.lines = [
            f'def convert(self) -> "{self.target_cls.name}":',
            f"    d = {{}}",
        ]
        self.methods: dict[str, Callable] = {}

    def get_source(self, name: str) -> str:
        return f"self.{name}"

    def _add_line(self, left_side: str, right_side: str, indent=4) -> None:
        self.lines.append(f'{" "*indent}d["{left_side}"] = {right_side}')

    def is_mappable_to(self, SourceCls, TargetCls) -> bool:
        func_name = get_map_to_func_name(TargetCls)
        return hasattr(SourceCls, func_name)

    def add_function_call(self, target: FieldMeta, function: Callable) -> None:
        name = f"_{uuid4().hex}"
        if len(signature(function).parameters) == 0:
            self.methods[name] = cast(Callable, staticmethod(function))
        else:
            # already a method
            # TODO assert that there is only one parameter and that it is `self`
            self.methods[name] = function
        source = self.get_source(name)
        self._add_line(target.name, f"{source}()")

    def add_mapping(self, target: FieldMeta, source: Union[FieldMeta, Callable]) -> None:
        if isfunction(source):
            self.add_function_call(target, source)
        else:
            assert isinstance(source, FieldMeta)

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

            AssignmentCls: Optional[Type[Assignment]] = None

            # same type, just assign it
            if target.type == source.type:
                AssignmentCls = SimpleAssignment

            # different type, but also safe mappable
            elif self.is_mappable_to(source.type, target.type) and not (
                source.allow_none and target.disallow_none
            ):
                options.if_None = source.allow_none
                AssignmentCls = RecursiveAssignment

            # both are lists of safe mappable types
            elif (
                get_origin(source.type) is list
                and get_origin(target.type) is list
                and self.is_mappable_to(get_args(source.type)[0], get_args(target.type)[0])
            ):
                options.if_None = source.allow_none
                AssignmentCls = ListRecursiveAssignment

            if AssignmentCls is not None:
                assignment = AssignmentCls(source=source, target=target)
                self.lines.extend(assignment.create_code(options))
            else: # impossible
                raise TypeError(
                    f"{source} of '{self.source_cls.name}' cannot be converted to {target}"
                )

    def __str__(self) -> str:
        if self.target_cls._type == DataclassType.PYDANTIC and not self.target_cls.has_validators:
            return_statement = f"    return {self.target_cls.alias_name}.construct(**d)"
        else:
            return_statement = f"    return {self.target_cls.alias_name}(**d)"
        return "\n".join(self.lines + [return_statement])


def get_map_to_func_name(cls: Any) -> str:
    return f"_map_to_{cls.__name__}"


def get_var_name(fieldmeta: FieldMeta) -> str:
    return f"self.{fieldmeta.name}"
