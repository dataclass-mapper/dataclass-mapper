Provide extra context to mapping
--------------------------------

Sometimes you need additional infos for the target object, that you don't have stored in the source class.
With :func:`~dataclass_mapper.provide_with_extra` you can mark fields, so that no mapping is generated, and the field is filled using an ``extra`` dictionary that can be given to the :func:`~dataclass_mapper.map_to` function.

.. testsetup:: *

   >>> from dataclasses import dataclass, field
   >>> from enum import Enum, auto
   >>> from typing import List, Optional, Dict
   >>> from dataclass_mapper import mapper, mapper_from, map_to, enum_mapper, enum_mapper_from, init_with_default, assume_not_none, from_extra

.. doctest::

   >>> @dataclass
   ... class Customer:
   ...     id: int
   ...     name: str
   >>>
   >>> @dataclass
   ... class Bill:
   ...     id: int
   ...     customer: Customer
   >>>
   >>> @mapper(Customer, {"id": from_extra("customer_id")})
   ... @dataclass
   ... class Person:
   ...     name: str
   >>>
   >>> @mapper(Bill, {"id": from_extra("bill_id")})
   ... @dataclass
   ... class BillEntity:
   ...     customer: Person
   >>>
   >>> bill_entity = BillEntity(customer=Person("John Doe"))
   >>> map_to(bill_entity, Bill, extra={"bill_id": 1, "customer_id": 42})
   Bill(id=1, customer=Customer(id=42, name='John Doe'))


.. warning::
   Values given via the ``extra`` dictionary are not checked for their correct type.

.. warning::
   When using the :func:`~dataclass_mapper.map_to` function it is checked, if all the required fields (marked with :func:`~dataclass_mapper.from_extra`) are given.
   It will raise a ``TypeError`` in case some marked field has no value in the ``extra`` dictionary.

   Use this feature in moderation.
