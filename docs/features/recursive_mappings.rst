Recursive models
----------------

.. testsetup:: *

   >>> from dataclasses import dataclass, field
   >>> from enum import Enum, auto
   >>> from typing import List, Optional, Dict
   >>> from dataclass_mapper import mapper, mapper_from, map_to, enum_mapper, enum_mapper_from, init_with_default, assume_not_none, provide_with_extra
   >>> from pydantic import BaseModel, Field
   >>> from uuid import UUID
   >>> uuid4 = lambda: UUID('38fc07e1-677e-40ef-830c-00e284056dd8')

Given the following simple classes together with their mappings, you can build more powerful recusive mappings.

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
   >>> @dataclass
   ... class Item:
   ...     description: str
   ...     cnt: int
   >>>
   >>> @mapper(Item, {"description": "name"})
   ... @dataclass
   ... class OrderItem:
   ...     name: str
   ...     cnt: int

Here the dataclasses use other dataclasses as fields, either direct ``recipient: Contact`` (and ``recipient: Person``),
or even inside a list ``items: List[OrderItem]`` (and ``items: List[Item]``) or in dictionary values ``items_by_name: dict[str, OrderItem]`` (and ``items_by_name: dict[str, Item]``).
As there is a mapper defined from ``Contact`` to ``Person``, and also a mapper defined from ``OrderItem`` to ``Item``, the object ``custom_order`` can be recusively mapped.

.. doctest::

   >>> @dataclass
   ... class Order:
   ...     recipient: Person
   ...     items: List[Item]
   ...     items_by_name: Dict[str, Item]
   >>>
   >>> @mapper(Order)
   ... @dataclass
   ... class CustomOrder:
   ...     recipient: Contact
   ...     items: List[OrderItem]
   ...     items_by_name: Dict[str, OrderItem]
   >>>
   >>> custom_order = CustomOrder(
   ...     recipient=Contact(first_name="Barbara E.", surname="Rolfe"),
   ...     items=[OrderItem(name="fruit", cnt=3), OrderItem(name="sweets", cnt=5)],
   ...     items_by_name={"fruit": OrderItem(name="fruit", cnt=3), "sweets": OrderItem(name="sweets", cnt=5)}
   ... )
   >>> map_to(custom_order, Order) #doctest: +NORMALIZE_WHITESPACE
   Order(recipient=Person(name='Barbara E. Rolfe', age=45),
         items=[Item(description='fruit', cnt=3), Item(description='sweets', cnt=5)],
         items_by_name={'fruit': Item(description='fruit', cnt=3), 'sweets': Item(description='sweets', cnt=5)})

.. warning::
   At the moment it's not possible to create cyclic mappings.
