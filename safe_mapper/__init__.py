__version__ = "0.5.0"

from .mapping_method import Other
from .safe_mapper import map_to, safe_mapper, safe_mapper_from

USE_DEFAULT = Other.USE_DEFAULT

__all__ = ["map_to", "safe_mapper", "safe_mapper_from", "USE_DEFAULT"]
