from inspect import signature
from typing import Callable, Dict, cast
from uuid import uuid4

from ..fieldmeta import FieldMeta


class FunctionAssignment:
    def __init__(self, function: Callable, target: FieldMeta, methods: Dict[str, Callable]):
        self.function = function
        self.target = target
        self.methods = methods

    def right_side(self) -> str:
        name = f"_{uuid4().hex}"
        if len(signature(self.function).parameters) == 0:
            self.methods[name] = cast(Callable, staticmethod(self.function))
        else:
            # already a method
            # TODO assert that there is only one parameter and that it is `self`
            self.methods[name] = self.function
        return f"self.{name}()"
