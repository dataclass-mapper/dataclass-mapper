__version__ = "1.0.2"

from .mapper import map_to, mapper, mapper_from
from .mapping_method import Spezial

USE_DEFAULT = Spezial.USE_DEFAULT
IGNORE_MISSING_MAPPING = Spezial.IGNORE_MISSING_MAPPING

__all__ = ["map_to", "mapper", "mapper_from", "USE_DEFAULT", "IGNORE_MISSING_MAPPING"]
