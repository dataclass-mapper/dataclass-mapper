Type safety
===========

The library will perform a lot of checks when creating a mapping.
All these checks already happen during the definition of the mapper, they are not run every single time when converting an instance of one class to an instance of another class.

.. testsetup:: *

   >>> from dataclasses import dataclass
   >>> from enum import Enum, auto
   >>> from typing import Optional
   >>> from dataclass_mapper import mapper, mapper_from, map_to, enum_mapper, enum_mapper_from, init_with_default
   >>> from pydantic import BaseModel, Field, validator

Missing fields check
--------------------

.. doctest::

   >>> @dataclass
   ... class Person:
   ...     name: str
   >>>
   >>> @mapper(Person)
   ... @dataclass
   ... class Contact:
   ...     surname: str
   ...     first_name: str
   Traceback (most recent call last):
     File "dataclass_mapper/mapper.py", line 55, in _make_mapper
       raise ValueError(
   ValueError: 'name' of 'Person' has no mapping in 'Contact'

The field ``name`` in the target class ``Person`` doesn't have an equivalent in the source class ``Contact``.
The library complains it.

This happens also when the field has a default value

.. doctest::

   >>> @dataclass
   ... class Foo:
   ...     x: int = 42
   >>>
   >>> @mapper(Foo)
   ... @dataclass
   ... class Bar:
   ...     pass
   Traceback (most recent call last):
     File "dataclass_mapper/mapping_method.py", line 55, in add_mapping
       raise ValueError(
   ValueError: 'x' of 'Foo' has no mapping in 'Bar'

However you can use the default value by using ``init_with_default``. This needs to be done explicitly.

.. doctest::

   >>> @mapper(Foo, {"x": init_with_default()})
   ... @dataclass
   ... class Bar:
   ...     pass

Field name checks
-----------------

.. doctest::

   >>> @mapper(Person, {"name": "surname", "first_name": "first_name"})
   ... @dataclass
   ... class Contact:
   ...     surname: str
   ...     first_name: str
   Traceback (most recent call last):
     File "dataclass_mapper/mapper.py", line 60, in _make_mapper
       raise ValueError(
   ValueError: 'first_name' of mapping in 'Contact' doesn't exist in 'Person'
   >>>
   >>> @mapper(Person, {"name": "surname", "name": "name"})
   ... @dataclass
   ... class Contact:
   ...     surname: str
   ...     first_name: str
   Traceback (most recent call last):
     File "dataclass_mapper/mapper.py", line 60, in _make_mapper
       raise ValueError(
   ValueError: 'name' of mapping in 'Contact' doesn't exist in 'Contact'

Here we tried to map the ``first_name`` parameter, however the target class ``Person`` doesn't have a ``first_name`` parameter.
And we tried to map the ``name`` parameter, however the source class ``Contact`` doesn't have a ``name`` parameter.

Type checks
-----------

.. doctest::

   >>> @dataclass
   ... class Contract:
   ...     full_time: bool
   ...     salary: int
   >>>
   >>> @mapper(Contract)
   ... @dataclass
   ... class EmploymentAgreement:
   ...     full_time: str  # "y" or "n"
   ...     salary: Optional[int]
   Traceback (most recent call last):
     File "dataclass_mapper/mapping_method.py", line 154, in add_mapping
       raise TypeError(
   TypeError: 'full_time' of type 'str' of 'EmploymentAgreement' cannot be converted to 'full_time' of type 'bool'

Here both classes use different types for the fields.
The library cannot map the field ``full_time`` of type ``str`` to a ``bool``.

.. doctest::

   >>> @mapper(Contract)
   ... @dataclass
   ... class EmploymentAgreement:
   ...     full_time: bool
   ...     salary: Optional[int]
   Traceback (most recent call last):
     File "dataclass_mapper/mapping_method.py", line 154, in add_mapping
       raise TypeError(
   TypeError: 'salary' of type 'Optional[int]' of 'EmploymentAgreement' cannot be converted to 'salary' of type 'int'

Here the library complains about the mapping an optional field to an non-optional one.
The other way around would be fine however.
