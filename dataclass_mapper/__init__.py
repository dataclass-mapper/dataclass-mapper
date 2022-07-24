__version__ = "0.5.0"

from .mapper import map_to, mapper, mapper_from
from .mapping_method import Other

USE_DEFAULT = Other.USE_DEFAULT

__all__ = ["map_to", "mapper", "mapper_from", "USE_DEFAULT"]
