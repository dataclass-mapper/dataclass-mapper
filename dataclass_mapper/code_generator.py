from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Union


class Expression(ABC):
    @abstractmethod
    def __str__(self) -> str:
        ...

    def equals(self, other: "Expression") -> "Expression":
        return Equals(self, other)

    def is_(self, other: "Expression") -> "Expression":
        return Is(self, other)

    def is_not(self, other: "Expression") -> "Expression":
        return IsNot(self, other)

    def in_(self, other: "Expression") -> "Expression":
        return In(self, other)

    def not_in_(self, other: "Expression") -> "Expression":
        return NotIn(self, other)



@dataclass
class Equals(Expression):
    left: Expression
    right: Expression

    def __str__(self) -> str:
        return f"{self.left} == {self.right}"


@dataclass
class Is(Expression):
    left: Expression
    right: Expression

    def __str__(self) -> str:
        return f"{self.left} is {self.right}"


@dataclass
class IsNot(Expression):
    left: Expression
    right: Expression

    def __str__(self) -> str:
        return f"{self.left} is not {self.right}"


@dataclass
class In(Expression):
    left: Expression
    right: Expression

    def __str__(self) -> str:
        return f"{self.left} in {self.right}"


@dataclass
class NotIn(Expression):
    left: Expression
    right: Expression

    def __str__(self) -> str:
        return f"{self.left} not in {self.right}"


@dataclass
class Variable(Expression):
    name: str

    def __str__(self) -> str:
        return self.name


NONE = Variable("None")


@dataclass
class StringValue(Expression):
    value: str

    def __str__(self) -> str:
        return f'"{self.value}"'


@dataclass
class DictLookup(Expression):
    dict_name: Union[str, Expression]
    key: Union[str, Expression]

    def __str__(self) -> str:
        if isinstance(self.key, str):
            return f'{self.dict_name}["{self.key}"]'
        else:
            return f'{self.dict_name}[{self.key}]'


@dataclass
class AttributeLookup(Expression):
    obj: Union[str, Expression]
    attribute: Union[str, Expression]

    def __str__(self) -> str:
        return f"{self.obj}.{self.attribute}"


@dataclass
class TernaryOperator(Expression):
    condition: Expression
    true_case: Expression
    false_case: Expression

    def __str__(self) -> str:
        return f"{self.true_case} if {self.condition} else {self.false_case}"


@dataclass
class ListComprehension(Expression):
    expr: Expression
    iter_var: Variable
    container: Expression

    def __str__(self) -> str:
        return f"[{self.expr} for {self.iter_var} in {self.container}]"


@dataclass
class DictComprehension(Expression):
    key_expr: Expression
    value_expr: Expression
    key_var: Variable
    value_var: Variable
    container: Expression

    def __str__(self) -> str:
        return (
            f"{{{self.key_expr}: {self.value_expr} for {self.key_var}, {self.value_var} in {self.container}.items()}}"
        )
        # TODO: does {{ }} work if you use it multiple times in f-strings


@dataclass
class FunctionCall(Expression):
    function_name: str
    parameters: List[Expression]

    def __str__(self) -> str:
        parameters = ", ".join(str(param) for param in self.parameters)
        return f"{self.function_name}({parameters})"


@dataclass
class MethodCall(Expression):
    object_name: Expression
    method_name: str
    parameters: List[Expression]

    def __str__(self) -> str:
        parameters = ", ".join(str(param) for param in self.parameters)
        return f"{self.object_name}.{self.method_name}({parameters})"


class Statement(ABC):
    @abstractmethod
    def to_string(self, indent: int) -> str:
        ...


class Pass(Statement):
    def to_string(self, indent: int) -> str:
        return f"{' '*indent}pass"


@dataclass
class Assignment(Statement):
    name: Union[str, Expression]
    rhs: Union[str, Expression]

    def to_string(self, indent: int) -> str:
        return f"{' '*indent}{self.name} = {self.rhs}"


class Block(Statement):
    def __init__(self, *statements: Statement):
        self.statements = list(statements)

    def append(self, statement: Statement) -> None:
        self.statements.append(statement)

    def to_string(self, indent: int) -> str:
        return "\n".join(statement.to_string(indent) for statement in self.statements)

    def __bool__(self) -> bool:
        return bool(self.statements)


@dataclass
class Raise(Statement):
    exception: str

    def to_string(self, indent: int) -> str:
        return f"{' '*indent}raise {self.exception}"


@dataclass
class IfElse(Statement):
    condition: Union[str, Expression]
    if_block: Statement
    else_block: Optional[Statement] = None

    def to_string(self, indent: int) -> str:
        lines: List[str] = []
        lines.append(f"{' '*indent}if {self.condition}:")
        lines.append(self.if_block.to_string(indent + 4))
        if self.else_block:
            lines.append(f"{' '*indent}else:")
            lines.append(self.else_block.to_string(indent + 4))
        return "\n".join(lines)


@dataclass
class Return(Statement):
    rhs: Union[str, Expression]

    def to_string(self, indent: int) -> str:
        return f"{' '*indent}return {self.rhs}"


@dataclass
class Function(Statement):
    name: str
    args: str
    return_type: str
    body: Block

    def to_string(self, indent: int) -> str:
        return f'{" "*indent}def {self.name}({self.args}) -> "{self.return_type}":\n{self.body.to_string(indent+4)}'
