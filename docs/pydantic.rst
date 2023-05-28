Pydantic models
===============

The library can also handle Pydantic's models, and map to them and from them.

It supports all the other features discussed in :doc:`features` or :doc:`enums`.

It supports both the old Pydantic version 1.x and the Rust rewrite 2.x.

Pydantic v2
-----------

For performance reasons it will use Pydantic's ``.model_construct`` class method to construct objects.
However it will fall back to the normal, slow initializer, when required (e.g. when the Pydantic model has validators that modify the model).

Additionally it can work with ``alias`` fields, and also with the ``populate_by_name`` configuration.

.. testsetup:: *

   >>> from dataclasses import dataclass, field
   >>> from enum import Enum, auto
   >>> from typing import Optional
   >>> from dataclass_mapper import mapper, mapper_from, map_to, enum_mapper, enum_mapper_from, init_with_default, assume_not_none
   >>> from pydantic import BaseModel, Field
   >>> import pytest
   >>> from dataclass_mapper.implementations.pydantic_v1 import pydantic_version
   >>> if pydantic_version() < (2, 0, 0):
   ...     pytest.skip("V2 validators syntax", allow_module_level=True)
   >>> from pydantic import field_validator

.. doctest::

   >>> class Animal(BaseModel):
   ...     name: str
   ...     greeting: str = Field(alias="greetingSound")
   ... 
   ...     @field_validator("greeting")
   ...     def repeat_greeting(cls, v):
   ...         return " ".join([v] * 3)
   >>>
   >>> @mapper(Animal)
   ... @dataclass
   ... class Pet:
   ...     name: str
   ...     greeting: str
   >>>
   >>> rocky = Pet(name="Rocky", greeting="Woof")
   >>> map_to(rocky, Animal)
   Animal(name='Rocky', greeting='Woof Woof Woof')

Pydantic also remembers which optional fields are set, and which are unset (with default ``None``).
This might be useful, if you want to distinguish if user explicitely set the value ``None``, or if they didn't set it all all (e.g. setting it explicitely could mean deleting the value in a database).
This library will remember which fields are set, and are unset.

.. doctest::

   >>> class Foo(BaseModel):
   ...     x: Optional[float] = None
   ...     y: Optional[int] = None
   ...     z: Optional[bool] = None
   >>>
   >>> @mapper(Foo)
   ... class Bar(BaseModel):
   ...     x: Optional[float] = None
   ...     y: Optional[int] = None
   ...     z: Optional[bool] = None
   >>>
   >>> bar = Bar(x=1.23, z=None)
   >>> sorted(bar.model_fields_set)
   ['x', 'z']
   >>> foo = map_to(bar, Foo)
   >>> foo
   Foo(x=1.23, z=None, y=None)
   >>> sorted(foo.model_fields_set)
   ['x', 'z']

.. include:: pydantic_v1.rst
