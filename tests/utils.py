import ast
from typing import Union

Code = Union[str, ast.expr, ast.stmt, ast.mod]


def assert_ast_equal(code1: Code, code2: Code) -> None:
    ast1 = ast.dump(get_unified_ast(code1), indent=2)
    ast2 = ast.dump(get_unified_ast(code2), indent=2)

    assert ast1 == ast2


def get_unified_ast(code: Code) -> ast.mod:
    if isinstance(code, ast.mod):
        return code
    elif isinstance(code, ast.stmt):
        return ast.Module(body=[code], type_ignores=[])
    elif isinstance(code, ast.expr):
        return ast.Module(body=[ast.Expr(code)], type_ignores=[])
    else:
        return ast.parse(code)
