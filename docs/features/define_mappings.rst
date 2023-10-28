Define mappings
---------------

Mapping by field names
^^^^^^^^^^^^^^^^^^^^^^

.. testsetup:: *

   >>> from dataclasses import dataclass, field
   >>> from enum import Enum, auto
   >>> from typing import List, Optional, Dict
   >>> from dataclass_mapper import mapper, mapper_from, map_to, enum_mapper, enum_mapper_from, init_with_default, assume_not_none, provide_with_extra
   >>> from pydantic import BaseModel, Field
   >>> from uuid import UUID
   >>> uuid4 = lambda: UUID('38fc07e1-677e-40ef-830c-00e284056dd8')

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

With the ``mapping`` parameter it's possible to define how the fields in the target class are filled.
Here we defining a mapper function from the ``Contact`` class to the `Person` class.
By specifying the mapping ``{'"name": "surname"}`` (in the order ``{"target_field": "source_field"}``) the field ``name`` in the target class ``Person`` will be filled with the value of the ``surname`` of the source class ``Contact``.
The ``age`` will be mapped automatically, as the field name ``age`` and the type ``int`` are identically in both classes.
The additional field ``first_name`` in the ``Contact`` class will just be ignored.

.. note::
   A mapping is not bidirectional.
   Here you can only map from ``Contact`` instances to ``Person`` instances, but not the other way.
   To also have a mapping from ``Person`` to ``Contact``, we would need to add a ``@mapper(Contact)`` decorator to ``Person``, or a ``@mapper_from`` to ``Contact`` (see `Mapping from another class`_).

.. note::
   It is checked if the types of the fields are compatible, i.e. if the target field allows all the type options of the source field.
   E.g. it is allowed to map from a ``str`` field to a ``Union[str, int]`` field or to an ``Optional[str]`` field, but not the other way around.
   You can loosen up those checks or disable them with the methods described in `Optional source fields`_ and `Custom conversion functions`_.

Mapping from another class
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. doctest::

   >>> @dataclass
   ... class OrderItem:
   ...     name: str
   ...     cnt: int
   >>>
   >>> @mapper_from(OrderItem, {"description": "name"})
   ... @dataclass
   ... class Item:
   ...     description: str
   ...     cnt: int
   >>>
   >>> order_item = OrderItem(name="fruit", cnt=5)
   >>> map_to(order_item, Item)
   Item(description='fruit', cnt=5)

Here we added a decorator ``@mapper_from(OrderItem)`` to the ``Item`` class.
That defines a mapper from ``OrderItem`` instances to ``Order`` instances.
The order of the mapping parameters is the same, it's ``{"target_field": "source_field"}``,
only difference is that the target class is now the class that is decorated.

.. note::
   It's also possible to add multiple decorators to one dataclass.
   E.g. it is possible to add a ``mapper`` and a ``mapper_from`` in order to have mappers in both directions.
