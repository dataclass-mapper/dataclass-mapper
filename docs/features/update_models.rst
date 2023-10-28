Update models
-------------

You can also update existing models.
With ``map_to`` you can simply overwrite the attributes that the normal mapping definition defines.

.. testsetup:: *

   >>> from dataclasses import dataclass, field
   >>> from enum import Enum, auto
   >>> from typing import List, Optional, Dict
   >>> from dataclass_mapper import mapper, mapper_from, map_to, enum_mapper, enum_mapper_from, init_with_default, assume_not_none, provide_with_extra, ignore
   >>> from pydantic import BaseModel, Field
   >>> from uuid import UUID
   >>> uuid4 = lambda: UUID('38fc07e1-677e-40ef-830c-00e284056dd8')
   >>> id = lambda _: 139772781422736

.. doctest::

   >>> @dataclass
   ... class OrderItem:
   ...     name: str
   ...     cnt: int
   >>>
   >>> @mapper(OrderItem)
   ... @dataclass
   ... class OrderItemNew:
   ...     name: str
   ...     cnt: int
   >>>
   >>> order = OrderItem(name="Apple", cnt=5)
   >>> id(order)
   139772781422736
   >>>
   >>> pearOrder = OrderItemNew(name="Pear", cnt=3)
   >>> map_to(pearOrder, order)
   >>> order
   OrderItem(name='Pear', cnt=3)
   >>> id(order)
   139772781422736

Sometimes you only want to overwrite a subset of fields, and leave the other values as is.
Per default the automapper will complain, if any required fields are ignored in the mapping.
However you can loosen that check, if you specify that a mapping is only meant for updates with ``only_update=True``, and not for creating new objects.

.. doctest::

   >>> @mapper(OrderItem, {"name": ignore()}, only_update=True)
   ... @dataclass
   ... class OrderItemUpdate:
   ...     cnt: int
   >>>
   >>> countUpdate = OrderItemUpdate(cnt=10)
   >>> map_to(countUpdate, order)
   >>> order
   OrderItem(name='Pear', cnt=10)


.. warning::
   This only works for regular fields.
   If your model is recursive (contains fields of other dataclasses), it will create new entities of those recursive fields and replace them.
