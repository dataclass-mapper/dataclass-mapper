__version__ = "1.0.2"

from .mapper import map_to, mapper, mapper_from
from .mapping_method import Other

USE_DEFAULT = Other.USE_DEFAULT

__all__ = ["map_to", "mapper", "mapper_from", "USE_DEFAULT"]
