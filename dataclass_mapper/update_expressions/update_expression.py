from abc import ABC, abstractmethod
from typing import List, Type

from dataclass_mapper.code_generator import Expression
from dataclass_mapper.exceptions import UpdatingNotPossibleError
from dataclass_mapper.fieldtypes import FieldType


class UpdateExpression(ABC):
    all_update_expressions: List[Type["UpdateExpression"]] = []

    def __init_subclass__(cls: Type["UpdateExpression"]):
        cls.all_update_expressions.append(cls)

    @abstractmethod
    def is_applicable_to_outer(self, source: FieldType, target: FieldType) -> bool:
        """Checks, if the most outer layer is applicable."""

    @abstractmethod
    def update_expression(
        self, source: FieldType, target: FieldType, source_exp: Expression, target_exp: Expression, recursion_depth: int
    ) -> Expression:
        """Creates the expression (that updates from source type to target type)."""


def map_update_expression(
    source: FieldType, target: FieldType, source_exp: Expression, target_exp: Expression, recursion_depth: int
) -> Expression:
    for update_expression_creator in UpdateExpression.all_update_expressions:
        if update_expression_creator().is_applicable_to_outer(source, target):
            return update_expression_creator().update_expression(
                source, target, source_exp, target_exp, recursion_depth
            )

    raise UpdatingNotPossibleError(source, target, recursion_depth)
