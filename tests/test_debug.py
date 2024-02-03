import re
import sys
from dataclasses import dataclass
from textwrap import dedent

import pytest

from dataclass_mapper import mapper_from
from dataclass_mapper.mapper import debug_map_codes


def prepare_expected_code(code: str) -> str:
    """remove empty lines and dedent"""
    return "\n".join(line for line in dedent(code).split("\n") if line)


@pytest.mark.skipif(
    sys.version_info < (3, 9), reason="3.8 doesn't have the ast.unparse function, so the result is different"
)
def test_debug_code():
    @dataclass
    class Source:
        x: int

    @mapper_from(Source)
    @dataclass
    class Target:
        x: int

    expected_create_code = prepare_expected_code(
        """
        def convert(self, extra: 'dict') -> 'Target':
            d = {}
            d['x'] = self.x
            return Target(**d)
        """
    )
    expected_update_code = prepare_expected_code(
        """
        def convert(self, extra: 'dict') -> 'Target':
            d = {}
            d['x'] = self.x
            return Target(**d)
        """
    )

    generated_create_code, generated_update_code = debug_map_codes(Source, Target)
    assert generated_create_code
    assert generated_update_code
    generated_create_code = re.sub(r"return _[a-z0-9]{32}", "return Target", generated_create_code)
    generated_update_code = re.sub(r"return _[a-z0-9]{32}", "return Target", generated_update_code)

    assert generated_create_code == expected_create_code
    assert generated_update_code == expected_update_code
