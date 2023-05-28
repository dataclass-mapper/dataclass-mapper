from ..utils import is_union_subtype
from .assignment import Assignment
from .utils import get_var_name


class SimpleAssignment(Assignment):
    def applicable(self) -> bool:
        return is_union_subtype(self.source.type, self.target.type)

    def right_side(self) -> str:
        return get_var_name(self.source)
