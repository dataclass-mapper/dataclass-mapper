from typing import Any

from .assignment import Assignment
from .utils import get_map_to_func_name, get_var_name, is_mappable_to


class RecursiveAssignment(Assignment):
    def applicable(self) -> bool:
        return is_mappable_to(self.source.type, self.target.type) and not (
            self.source.allow_none and self.target.disallow_none
        )

    def right_side(self) -> str:
        return self._get_map_func(get_var_name(self.source), target_cls=self.target.type)

    def _get_map_func(self, name: str, target_cls: Any) -> str:
        func_name = get_map_to_func_name(target_cls)
        return f"{name}.{func_name}()"
