from .assignment import Assignment
from .utils import get_var_name


class SimpleAssignment(Assignment):
    def applicable(self) -> bool:
        return bool(self.target.type == self.source.type)

    def right_side(self) -> str:
        return get_var_name(self.source)
