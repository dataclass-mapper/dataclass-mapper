__version__ = "1.3.0"

from .mapper import enum_mapper, enum_mapper_from, map_to, mapper, mapper_from
from .mapping_method import Spezial

USE_DEFAULT = Spezial.USE_DEFAULT
IGNORE_MISSING_MAPPING = Spezial.IGNORE_MISSING_MAPPING

__all__ = [
    "map_to",
    "mapper",
    "mapper_from",
    "enum_mapper",
    "enum_mapper_from",
    "USE_DEFAULT",
    "IGNORE_MISSING_MAPPING",
]
