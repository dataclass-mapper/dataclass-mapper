.. _CustomConversionFunctions:

Custom conversion functions
---------------------------

.. testsetup:: *

   >>> from dataclasses import dataclass, field
   >>> from enum import Enum, auto
   >>> from typing import List, Optional, Dict
   >>> from dataclass_mapper import mapper, mapper_from, map_to, enum_mapper, enum_mapper_from, init_with_default, assume_not_none, provide_with_extra

.. doctest::

   >>> @dataclass
   ... class Person:
   ...     name: str
   ...     age: int
   >>>
   >>> @mapper(Person, {"age": lambda: 45, "name": lambda self: f"{self.first_name} {self.surname}"})
   ... @dataclass
   ... class Contact:
   ...     surname: str
   ...     first_name: str
   >>>
   >>> contact = Contact(first_name="Jesse", surname="Cross")
   >>> map_to(contact, Person)
   Person(name='Jesse Cross', age=45)

It's possible to add custom functions to mappings.

In case the function takes no arguments, the function just behaves like setting a constant.
The first function ``lambda: 45`` has no parameters and just returns the constant ``45``, so the age will always be initialized with ``45``.

In case the function has one parameter, the source object will be passed and you can initialize the field however you want.
In the second function ``lambda self: f"{self.first_name} {self.surname}"`` there is one parameter ``self`` (resembling a class method), and it combines the ``first_name`` and ``surname`` into a string and initialize the field ``name`` with it.

.. warning::
   Custom conversion functions are not type-checked.
   So be careful when using them.
