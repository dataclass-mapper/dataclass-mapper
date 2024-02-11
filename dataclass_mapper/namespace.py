import sys
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class Namespace:
    locals: Dict[str, Any]
    globals: Dict[str, Any]


def get_namespace(parent_depth: int = 2) -> Namespace:
    """computes the locals and globals of a parent stack frame"""
    frame = sys._getframe(parent_depth)
    return Namespace(locals=frame.f_locals, globals=frame.f_globals)
