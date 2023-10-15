Architecture Constraints
------------------------

Technical Constraints
^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :stub-columns: 1

   *  -  Constraint
      -  Background and / or motivation

   *  -  Python version
      -  The library should be on usable on all officially supported versions since 3.8 (see `Status of Python Versions <https://devguide.python.org/versions/>`_).
         Therefore the library needs to be written with Python 3.8 compatible code.

Organizational Constraints
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :stub-columns: 1

   *  -  Constraint
      -  Background and / or motivation

   *  -  Team
      -  `Jakob Kogler <https://github.com/jakobkogler>`_

   *  -  Development Tools
      -  No particular IDE

   *  -  Test tools and test processes
      -  ``Mypy`` for static type checking, ``pytest`` for unit-tests, ``tox`` for testing the library with multiple Python versions.

   *  -  Open Source
      -  Source code is released on `Github <https://github.com/dataclass-mapper/dataclass-mapper/>`_ under the `MIT License <https://github.com/dataclass-mapper/dataclass-mapper/blob/main/LICENSE.md>`_.

   *  -  Distribution
      -  Library is bundled as wheel and published on `PyPI <https://pypi.org/project/dataclass-mapper/>`_.

Conventions
^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :stub-columns: 1

   *  -  Convention
      -  Background and / or motivation

   *  -  Architecture documentation
      -  According to `Arc42 <https://arc42.org/overview>`_.

   *  -  Coding guidelines
      -  Formatting according to ``black``, linting rules according to ``ruff``.
