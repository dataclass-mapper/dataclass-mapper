ADR 001: Write a new library
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Status
""""""

Accepted. December 10, 2022

Context
"""""""

For a closed-source project I needed a library that helped mapping between two dataclasses.
I already had some helper functions, that did parts of this library, but it felt unsafe, and mixed responsibilities (business logic and mappings) too much.

The basic requirements are more or less the requirements from :ref:`Requirements Overview`.

There are a couple of libraries out there, that perform some such tasks.

*  `odin <https://github.com/python-odin/odin>`_: A new dataclass implementation, where you can define mappings. But no support for ``dataclasses`` or ``pydantic``.
*  `object-mapper <https://github.com/marazt/object-mapper>`_: Similar mapping definitions, but no type validation. Also it's unmaintained, and only supports Python <=3.8.
*  `panamap <https://github.com/panamap-object-mapper/panamap>`_: Similar, but no type validation. Looks unmaintained.
*  `automapping <https://github.com/GabrielCpp/automapping>`_: Similar, but more a proof-of-concept library than a maintained implementation.
*  `py-automapper <https://github.com/anikolaienko/py-automapper>`_: Supports ``dataclasses``, ``pydantic`` and many more dataclass implementations. But no typing checks, and doesn't work for recursive objects.
*  `pydantic <https://docs.pydantic.dev>`_'s ORM Mode: too restricted when mapping between field with different names

Alternatively I can write a new library.

Decision
""""""""

Writing and maintaining a new library is hard work.
But since none of the other solutions satisfies the majority of the requirements, or is unmaintained, that's the only acceptable option.

Consequences
""""""""""""

Start writing a new library.
