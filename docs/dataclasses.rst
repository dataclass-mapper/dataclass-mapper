Python's dataclasses
====================

Python's ``dataclasses`` library is the most simple one.

.. testsetup:: *

   >>> from dataclasses import dataclass, field
   >>> from enum import Enum, auto
   >>> from typing import Optional
   >>> from dataclass_mapper import mapper, mapper_from, map_to, enum_mapper, enum_mapper_from, init_with_default, assume_not_none, ignore
   >>> import pytest
   >>> from dataclass_mapper.implementations.pydantic_v1 import pydantic_version

It understands normal fields, and additionally also ``init=False`` fields.
You can simple ignore the field, then the logic of ``__post_init__`` fills the field, or you can use a normal mapping and overwrite the field afterwards.

.. doctest::

   >>> @dataclass
   ... class Target:
   ...     x: int
   ...     y: int = field(init=False)
   ... 
   ...     def __post_init__(self):
   ...         self.y = self.x + 1
   >>>
   >>> @mapper(Target, {"y": ignore()})
   ... @dataclass
   ... class Source1:
   ...     x: int
   >>>
   >>> map_to(Source1(x=5), Target)
   Target(x=5, y=6)
   >>>
   >>> @mapper(Target)
   ... @dataclass
   ... class Source2:
   ...     x: int
   ...     y: int
   >>>
   >>> map_to(Source2(x=5, y=-1), Target)
   Target(x=5, y=-1)
