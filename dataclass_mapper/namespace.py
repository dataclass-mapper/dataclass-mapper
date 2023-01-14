import sys
from dataclasses import dataclass
from typing import Any


@dataclass
class Namespace:
    locals: dict[str, Any]
    globals: dict[str, Any]


def get_namespace(parent_depth: int = 2) -> Namespace:
    """computes the locals and globals of a parent stack frame"""
    frame = sys._getframe(parent_depth)
    return Namespace(locals=frame.f_locals, globals=frame.f_globals)
