import ast
import sys
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, List, Optional, Union


class Expression(ABC):
    store: bool = False

    def as_store(self) -> "Expression":
        new_ = deepcopy(self)
        new_.store = True
        return new_

    def get_ctx(self):
        if self.store:
            return ast.Store()
        else:
            return ast.Load()

    @abstractmethod
    def generate_ast(self) -> ast.expr: ...

    def is_(self, other: "Expression") -> "Expression":
        return Compare(self, other, ast.Is())

    def is_not(self, other: "Expression") -> "Expression":
        return Compare(self, other, ast.IsNot())

    def in_(self, other: "Expression") -> "Expression":
        return Compare(self, other, ast.In())

    def not_in_(self, other: "Expression") -> "Expression":
        return Compare(self, other, ast.NotIn())


@dataclass
class Variable(Expression):
    name: str
    type_: Optional[Expression] = None

    def generate_ast(self) -> ast.expr:
        return ast.Name(id=self.name, ctx=self.get_ctx())

    def as_arg(self) -> "Arg":
        return Arg(name=self.name, type_=self.type_)


@dataclass
class Constant(Expression):
    value: Any

    def generate_ast(self) -> ast.expr:
        if sys.version_info < (3, 9):
            return ast.Constant(value=self.value, kind=None)
        else:
            return ast.Constant(value=self.value)


NONE = Constant(None)


@dataclass
class EmptyDict(Expression):
    def generate_ast(self) -> ast.expr:
        return ast.Dict(keys=[], values=[])


@dataclass
class Compare(Expression):
    left: Expression
    right: Expression
    operation: ast.cmpop

    def generate_ast(self) -> ast.expr:
        return ast.Compare(left=self.left.generate_ast(), ops=[self.operation], comparators=[self.right.generate_ast()])


@dataclass
class DictLookup(Expression):
    dictionary: Expression
    key: Expression

    def generate_ast(self) -> ast.expr:
        value = self.dictionary.generate_ast()
        if sys.version_info < (3, 9):
            slice = ast.Index(value=self.key.generate_ast())
        else:
            slice = self.key.generate_ast()

        return ast.Subscript(value=value, slice=slice, ctx=self.get_ctx())


@dataclass
class AttributeLookup(Expression):
    obj: Expression
    attribute: str

    def as_store(self) -> "Expression":
        """Empty attribute means, that there is no attribute lookup at all.
        So the as_store() hint needs to be handed over to the nested obj.
        """
        if self.attribute:
            return super().as_store()
        else:
            self.obj = self.obj.as_store()
            return self

    def generate_ast(self) -> ast.expr:
        if not self.attribute:
            return self.obj.generate_ast()
        return ast.Attribute(value=self.obj.generate_ast(), attr=self.attribute, ctx=self.get_ctx())


@dataclass
class TernaryOperator(Expression):
    condition: Expression
    true_case: Expression
    false_case: Expression

    def generate_ast(self) -> ast.expr:
        return ast.IfExp(
            test=self.condition.generate_ast(),
            body=self.true_case.generate_ast(),
            orelse=self.false_case.generate_ast(),
        )


@dataclass
class ListComprehension(Expression):
    expr: Expression
    iter_var: Variable
    container: Expression

    def generate_ast(self) -> ast.expr:
        return ast.ListComp(
            elt=self.expr.generate_ast(),
            generators=[
                ast.comprehension(
                    target=self.iter_var.as_store().generate_ast(),
                    iter=self.container.generate_ast(),
                    ifs=[],
                    is_async=0,
                )
            ],
        )


@dataclass
class Tuple(Expression):
    expressions: List[Expression]

    def generate_ast(self) -> ast.expr:
        return ast.Tuple(elts=[expr.generate_ast() for expr in self.expressions], ctx=ast.Load())


@dataclass
class SetComprehension(Expression):
    expr: Expression
    iter_var: Variable
    container: Expression

    def generate_ast(self) -> ast.expr:
        return ast.SetComp(
            elt=self.expr.generate_ast(),
            generators=[
                ast.comprehension(
                    target=self.iter_var.as_store().generate_ast(),
                    iter=self.container.generate_ast(),
                    ifs=[],
                    is_async=0,
                )
            ],
        )


@dataclass
class DictComprehension(Expression):
    key_expr: Expression
    value_expr: Expression
    key_var: Variable
    value_var: Variable
    container: Expression

    def generate_ast(self) -> ast.expr:
        return ast.DictComp(
            key=self.key_expr.generate_ast(),
            value=self.value_expr.generate_ast(),
            generators=[
                ast.comprehension(
                    target=ast.Tuple(
                        elts=[self.key_var.as_store().generate_ast(), self.value_var.as_store().generate_ast()],
                        ctx=ast.Store(),
                    ),
                    iter=MethodCall(self.container, "items", []).generate_ast(),
                    ifs=[],
                    is_async=0,
                )
            ],
        )


@dataclass
class Keyword:
    value: Expression
    arg: Optional[str] = None

    def generate_ast(self) -> ast.keyword:
        return ast.keyword(value=self.value.generate_ast(), arg=self.arg)


@dataclass
class MethodCall(Expression):
    obj: Expression
    method_name: str
    args: List[Expression]
    keywords: List[Keyword] = field(default_factory=list)

    def generate_ast(self) -> ast.expr:
        return ast.Call(
            func=AttributeLookup(self.obj, self.method_name).generate_ast(),
            args=[arg.generate_ast() for arg in self.args],
            keywords=[keyword.generate_ast() for keyword in self.keywords],
        )


@dataclass
class FunctionCall(Expression):
    function: Expression
    args: List[Expression]
    keywords: List[Keyword] = field(default_factory=list)

    def generate_ast(self) -> ast.expr:
        return ast.Call(
            func=self.function.generate_ast(),
            args=[arg.generate_ast() for arg in self.args],
            keywords=[keyword.generate_ast() for keyword in self.keywords],
        )


class Statement(ABC):
    @abstractmethod
    def generate_ast(self) -> ast.stmt:  # TODO
        ...


@dataclass
class ExpressionStatement(Statement):
    expression: Expression

    def generate_ast(self) -> ast.stmt:
        return ast.Expr(value=self.expression.generate_ast())


class Pass(Statement):
    def generate_ast(self) -> ast.stmt:
        return ast.Pass()


@dataclass
class Assignment(Statement):
    lhs: Expression
    rhs: Expression

    def generate_ast(self) -> ast.stmt:
        targets = [self.lhs.as_store().generate_ast()]
        value = self.rhs.generate_ast()
        if sys.version_info < (3, 9):
            return ast.Assign(targets=targets, value=value, type_comment=None)
        else:
            return ast.Assign(targets=targets, value=value)


@dataclass
class Raise(Statement):
    exception: str
    message: str

    def generate_ast(self) -> ast.stmt:
        exc = ast.Call(
            func=ast.Name(id=self.exception, ctx=ast.Load()), args=[Constant(self.message).generate_ast()], keywords=[]
        )

        if sys.version_info < (3, 9):
            return ast.Raise(exc=exc, cause=None)
        else:
            return ast.Raise(exc=exc)


@dataclass
class IfElse(Statement):
    condition: Expression
    if_block: List[Statement]
    else_block: List[Statement] = field(default_factory=list)

    def generate_ast(self) -> ast.stmt:
        return ast.If(
            test=self.condition.generate_ast(),
            body=[stmt.generate_ast() for stmt in self.if_block],
            orelse=[stmt.generate_ast() for stmt in self.else_block],
        )


@dataclass
class Return:
    expression: Expression

    def generate_ast(self) -> ast.stmt:
        return ast.Return(value=self.expression.generate_ast())


@dataclass
class Arg:
    name: str
    type_: Optional[Expression] = None

    def generate_ast(self):
        annotation = None if self.type_ is None else self.type_.generate_ast()

        if sys.version_info < (3, 9):
            return ast.arg(arg=self.name, annotation=annotation, type_comment=None)
        else:
            return ast.arg(arg=self.name, annotation=annotation)


@dataclass
class Function(Statement):
    name: str
    args: List[Union[Arg, Variable]]
    return_type: Expression
    body: List[Any]

    def generate_ast(self) -> ast.stmt:
        name = self.name
        args = ast.arguments(
            args=[(arg if isinstance(arg, Arg) else arg.as_arg()).generate_ast() for arg in self.args],
            posonlyargs=[],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        )
        body = [stmt.generate_ast() for stmt in self.body] or [Pass().generate_ast()]
        returns = self.return_type.generate_ast()

        if sys.version_info < (3, 9):
            return ast.FunctionDef(
                name=name,
                args=args,
                body=body,
                decorator_list=[],
                returns=returns,
                type_comment=None,
            )
        elif sys.version_info < (3, 12):
            return ast.FunctionDef(
                name=name,
                args=args,
                body=body,
                decorator_list=[],
                returns=returns,
            )
        else:
            return ast.FunctionDef(name=name, args=args, body=body, decorator_list=[], returns=returns, type_params=[])


@dataclass
class Module:
    stmts: List[Any]

    def generate_ast(self) -> ast.Module:
        m = ast.Module(body=[stmt.generate_ast() for stmt in self.stmts], type_ignores=[])
        return ast.fix_missing_locations(m)
