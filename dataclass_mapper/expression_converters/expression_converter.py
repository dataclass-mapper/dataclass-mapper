from abc import ABC, abstractmethod
from typing import ClassVar, List, Type

from dataclass_mapper.code_generator import Expression
from dataclass_mapper.exceptions import ConvertingNotPossibleError
from dataclass_mapper.fieldtypes import FieldType


class ExpressionConverter(ABC):
    all_expression_converts: ClassVar[List[Type["ExpressionConverter"]]] = []

    def __init_subclass__(cls: Type["ExpressionConverter"]):
        cls.all_expression_converts.append(cls)

    @abstractmethod
    def is_applicable_to_outer(self, source: FieldType, target: FieldType) -> bool:
        """Checks, if the most outer layer is applicable.
        E.g. the :class:`OptionalExpressionConverter` is applicable to the field with
        type ``Optional[List[int]]``, while the :class:`ListExpressionConverter` isn't."""

    @abstractmethod
    def map_expression(
        self, source: FieldType, target: FieldType, source_exp: Expression, recursion_depth: int
    ) -> Expression:
        """Creates the expression (that converts from source type to target type)."""

    @abstractmethod
    def is_assignable(self, source: FieldType, target: FieldType) -> bool:
        """Essentially can you write ``target = source``.
        The types can be slightly different, but should be assignable.
        E.g. if target is of type ``Optional[FooBase]`` and ``source is of
        type ``Foo`` (inheriting from ``FooBase``), it should return true.
        """


def map_expression(source: FieldType, target: FieldType, source_exp: Expression, recursion_depth: int) -> Expression:
    for expression_converter in ExpressionConverter.all_expression_converts:
        if expression_converter().is_applicable_to_outer(source, target):
            return expression_converter().map_expression(source, target, source_exp, recursion_depth)

    raise ConvertingNotPossibleError(source, target, recursion_depth)


def is_assignable(source: FieldType, target: FieldType) -> bool:
    """Essentially can you write ``target = source``.
    The types can be slightly different, but should be assignable.
    E.g. if target is of type ``Optional[FooBase]`` and ``source is of
    type ``Foo`` (inheriting from ``FooBase``), it should return true.
    """
    for expression_converter in ExpressionConverter.all_expression_converts:
        if expression_converter().is_assignable(source, target):
            return True

    return False
