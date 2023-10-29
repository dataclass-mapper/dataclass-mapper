Mapping by field names
----------------------

With the ``mapping`` parameter it's possible to define how the fields in the target class are filled.

.. testsetup:: *

   >>> from dataclasses import dataclass, field
   >>> from enum import Enum, auto
   >>> from typing import List, Optional, Dict
   >>> from dataclass_mapper import mapper, mapper_from, map_to, enum_mapper, enum_mapper_from, init_with_default, assume_not_none, provide_with_extra, create_mapper

.. doctest::

   >>> @dataclass
   ... class Person:
   ...     name: str
   ...     age: int
   >>>
   >>> @mapper(Person, {"name": "surname"})
   ... @dataclass
   ... class Contact:
   ...     surname: str
   ...     first_name: str
   ...     age: int
   >>>
   >>> contact = Contact(first_name="Jesse", surname="Cross", age=50)
   >>> map_to(contact, Person)
   Person(name='Cross', age=50)

By specifying the mapping ``{'"name": "surname"}`` (in the order ``{"target_field": "source_field"}``) the field ``name`` in the target class ``Person`` will be filled with the value of the ``surname`` of the source class ``Contact``.
The ``age`` will be mapped automatically, as the field name ``age`` and the type ``int`` are identically in both classes.
The additional field ``first_name`` in the ``Contact`` class will just be ignored.
