import re
from typing import Tuple


def parse_version(version: str) -> Tuple[int, int, int]:
    if m := re.search(r"(\d+)\.(\d+)\.(\d+)", version):
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return (0, 0, 0)
