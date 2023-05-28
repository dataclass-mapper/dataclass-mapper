from inspect import signature
from typing import Any, Callable, Dict, Union, cast
from uuid import uuid4

from ..fieldmeta import FieldMeta

CallableWithMax1Parameter = Union[Callable[[], Any], Callable[[Any], Any]]


class FunctionAssignment:
    def __init__(
        self, function: CallableWithMax1Parameter, target: FieldMeta, methods: Dict[str, Callable], target_cls_name: str
    ):
        self.function = function
        self.target = target
        self.methods = methods
        self.target_cls_name = target_cls_name

    def right_side(self) -> str:
        name = f"_{uuid4().hex}"
        if (parameter_cnt := len(signature(self.function).parameters)) < 2:
            if parameter_cnt == 0:
                self.methods[name] = cast(Callable, staticmethod(cast(Callable, self.function)))
            else:
                self.methods[name] = self.function
            return f"self.{name}()"

        # can only happen, if the typing annotation fails (e.g. because mypy is not installed)
        raise ValueError(
            f"'{self.target.name}' of '{self.target_cls_name}' cannot be mapped "
            "using a factory with more than one parameter"
        )
