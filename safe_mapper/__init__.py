__version__ = "0.4.2"

from .mapping_method import Default, DefaultFactory
from .safe_mapper import map_to, safe_mapper, safe_mapper_from

__all__ = ["map_to", "safe_mapper", "safe_mapper_from", "Default", "DefaultFactory"]
