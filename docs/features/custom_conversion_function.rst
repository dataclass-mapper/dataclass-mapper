.. _CustomConversionFunctions:

Custom conversion functions
---------------------------

It is possible to use a callable during a field mapping.
That can be a function, a lambda, or a callable object.

.. testsetup:: *

   >>> from dataclasses import dataclass, field
   >>> from enum import Enum, auto
   >>> from typing import List, Optional, Dict
   >>> from dataclass_mapper import mapper, mapper_from, map_to, enum_mapper, enum_mapper_from, init_with_default, assume_not_none, create_mapper

.. doctest::

   >>> @dataclass
   ... class Person:
   ...     name: str
   ...     age: int
   >>>
   >>> @dataclass
   ... class Contact:
   ...     surname: str
   ...     first_name: str
   >>>
   >>> def compute_full_name(contact: Contact) -> str:
   ...     return f"{contact.first_name} {contact.surname}"
   >>>
   >>> create_mapper(Contact, Person, {"age": lambda: 45, "name": compute_full_name})
   >>> 
   >>> contact = Contact(first_name="Jesse", surname="Cross")
   >>> map_to(contact, Person)
   Person(name='Jesse Cross', age=45)

In case the function takes no arguments, the function just behaves like setting a constant.
The first function ``lambda: 45`` has no parameters and just returns the constant ``45``, so the age will always be initialized with ``45``.

In case the function has one parameter, the source object will be passed and you can initialize the field however you want.
In the second function ``compute_full_name`` takes one parameter ``contact: Contact``, and combines the ``first_name`` and ``surname`` into a string and initialize the field ``name`` with it.

In case the function or callable object is annotated with types, the types will be checked.
E.g. if the function ``compute_full_name`` returns an ``int`` or takes the a parameter of type ``Person``, it will produce an ``TypeError`` during the creation of the mapper.

.. warning::
   Always use typed functions or typed callable objects.
   Untyped functions, untyped callable objects or just lambas (which cannot be types) will not by type-checked by the library.
   Especially a lambda can return anything, and the library will not check the type during the conversion!
