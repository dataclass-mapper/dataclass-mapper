from typing import get_args, get_origin

from .recursive import RecursiveAssignment
from .utils import get_var_name, is_mappable_to


class ListRecursiveAssignment(RecursiveAssignment):
    def applicable(self) -> bool:
        return (
            get_origin(self.source.type) is list
            and get_origin(self.target.type) is list
            and is_mappable_to(get_args(self.source.type)[0], get_args(self.target.type)[0])
        )

    def right_side(self) -> str:
        list_item_type = get_args(self.target.type)[0]
        return f'[{self._get_map_func("x", target_cls=list_item_type)} for x in {get_var_name(self.source)}]'
