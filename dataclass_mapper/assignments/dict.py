from typing import get_args, get_origin

from .recursive import RecursiveAssignment
from .utils import get_var_name, is_mappable_to


class DictRecursiveAssignment(RecursiveAssignment):
    def applicable(self) -> bool:
        if not (get_origin(self.source.type) is dict and get_origin(self.target.type) is dict):
            return False

        source_key_type, source_value_type = get_args(self.source.type)
        target_key_type, target_value_type = get_args(self.target.type)
        return source_key_type == target_key_type and is_mappable_to(source_value_type, target_value_type)

    def right_side(self) -> str:
        target_value_type = get_args(self.target.type)[1]
        extra_str = self.extra_str() + ".get(k, {})"
        value_map_expression = self._get_map_func("v", target_cls=target_value_type, extra_str=extra_str)
        return f"{{k: {value_map_expression} for k, v in {get_var_name(self.source)}.items()}}"
