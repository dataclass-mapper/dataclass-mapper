import ast
import sys
from typing import Union

Code = Union[str, ast.expr, ast.stmt, ast.mod]


def assert_ast_equal(code1: Code, code2: Code) -> None:
    ast1 = get_ast_dump(get_unified_ast(code1))
    ast2 = get_ast_dump(get_unified_ast(code2))
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


def get_ast_dump(ast_obj: ast.mod) -> str:
    if sys.version_info < (3, 9):
        return ast.dump(ast_obj)
    else:
        return ast.dump(ast_obj, indent=2)
