from .assignment import Assignment
from .dict import DictRecursiveAssignment
from .function import CallableWithMax1Parameter, FunctionAssignment
from .list import ListRecursiveAssignment
from .recursive import RecursiveAssignment
from .simple import SimpleAssignment
from .utils import get_map_to_func_name, get_mapupdate_to_func_name, get_var_name

__all__ = [
    "Assignment",
    "CallableWithMax1Parameter",
    "DictRecursiveAssignment",
    "SimpleAssignment",
    "RecursiveAssignment",
    "ListRecursiveAssignment",
    "FunctionAssignment",
    "get_var_name",
    "get_map_to_func_name",
    "get_mapupdate_to_func_name",
]
