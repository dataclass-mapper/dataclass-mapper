from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Union


class Expression(ABC):
    @abstractmethod
    def __str__(self) -> str:
        ...


@dataclass
class DictLookup(Expression):
    dict_name: Union[str, Expression]
    key: Union[str, Expression]

    def __str__(self) -> str:
        return f'{self.dict_name}["{self.key}"]'


@dataclass
class AttributeLookup(Expression):
    obj: Union[str, Expression]
    attribute: Union[str, Expression]

    def __str__(self) -> str:
        return f"{self.obj}.{self.attribute}"


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
