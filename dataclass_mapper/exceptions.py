from dataclasses import dataclass

from dataclass_mapper.fieldtypes import FieldType


@dataclass
class ConvertingNotPossibleError(Exception):
    source: FieldType
    target: FieldType
    recursion_depth: int


@dataclass
class UpdatingNotPossibleError(Exception):
    source: FieldType
    target: FieldType
    recursion_depth: int
