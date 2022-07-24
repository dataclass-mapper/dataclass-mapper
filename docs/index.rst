Welcome to dataclass-mapper's documentation!
============================================

Writing mapper methods between two similar dataclasses is boring and error-prone.
Much better to let a library auto-generate them for you.

This library makes sure that all fields of the target class are actually mapped to (already at the module import time), and also provides helper mappers for variables that don't change their names.
It supports Python's dataclasses and also Pydantic models.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
