Update models
-------------

Simple Updates
^^^^^^^^^^^^^^

You can also update existing models.
With ``map_to`` you can simply overwrite the attributes that the normal mapping definition defines.

.. testsetup:: *

   >>> from dataclasses import dataclass, field
   >>> from enum import Enum, auto
   >>> from typing import List, Optional, Dict
   >>> from dataclass_mapper import mapper, mapper_from, map_to, enum_mapper, enum_mapper_from, init_with_default, assume_not_none, ignore, MapperMode, update_only_if_set
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
   >>> order_item = OrderItem(name="Apple", cnt=5)
   >>> id(order_item)
   139772781422736
   >>>
   >>> map_to(OrderItemNew(name="Pear", cnt=3), order_item)
   >>> order_item
   OrderItem(name='Pear', cnt=3)
   >>> id(order_item)
   139772781422736

Partial Updates
^^^^^^^^^^^^^^^

Sometimes you only want to overwrite a subset of fields, and leave the other values as is.
Per default the automapper will complain, if any required fields are ignored in the mapping.
However you can loosen that check, if you specify that a mapping is only meant for updates with ``mapper_mode=MapperMode.UPDATE``, and not for creating new objects.

.. doctest::

   >>> @mapper(OrderItem, {"name": ignore()}, mapper_mode=MapperMode.UPDATE)
   ... @dataclass
   ... class OrderItemUpdate:
   ...     cnt: int
   >>>
   >>> map_to(OrderItemUpdate(cnt=10), order_item)
   >>> order_item
   OrderItem(name='Pear', cnt=10)

This also works in a limited way for simple recursive objects.

.. doctest::

  >>> @dataclass
  ... class Order:
  ...     item: OrderItem
  >>>
  >>> @mapper(Order, mapper_mode=MapperMode.UPDATE)
  ... @dataclass
  ... class OrderUpdate:
  ...     item: OrderItemUpdate
  >>>
  >>> order = Order(item=order_item)
  >>> order
  Order(item=OrderItem(name='Pear', cnt=10))
  >>>
  >>> map_to(OrderUpdate(item=OrderItemUpdate(cnt=92)), order)
  >>> order
  Order(item=OrderItem(name='Pear', cnt=92))

.. warning::
   However it doesn't work for any more complicated recursive objects.
   E.g. if your model fields are optional, or lists of recursive class objects.
   In those instances it will create new entities of those recursive fields and replace them.
   Notice, that this means, that for those recursive dataclasses the mapper needs to be defined with :py:enum:mem:`~dataclass_.MapperMode.CREATE` or :py:enum:mem:`~MapperMode.CREATE_AND_UPDATE`.
   
   If you really want to recursively update a field with a list of dataclasses, and don't recreate them (e.g. for ORM models), then you can :func:`~dataclass_mapper.ignore` them, and perform some custom updates after the main mapping is finished.

Optional Updates
^^^^^^^^^^^^^^^^

In some cases it makes sense, to allow the update model more freedom, and make all/some fields optional with the idea to only update those that are set instead of all.
In that case you need to apply the :func:`~dataclass_mapper.update_only_if_set` function.

.. doctest::

   >>> @dataclass
   ... class Contact:
   ...     name: str
   ...     age: int
   >>>
   >>> @mapper(Contact, {"name": update_only_if_set(), "age": update_only_if_set("new_age")}, mapper_mode=MapperMode.UPDATE)
   ... @dataclass
   ... class ContactUpdate:
   ...     name: Optional[str] = None
   ...     new_age: Optional[int] = None
   >>>
   >>> contact = Contact(name="Alice Space", age=20)
   >>> map_to(ContactUpdate(name="Alice Trance"), contact)
   >>> contact
   Contact(name='Alice Trance', age=20)
   >>>
   >>> map_to(ContactUpdate(new_age=21), contact)
   >>> contact
   Contact(name='Alice Trance', age=21)

.. note::
   With Pydantic you can archive something similar.
   It however concerns updating an optional field from another optional field.
   Pydantic models will remember, if you set a value explicitly or if it was set to ``None`` implicitly.
   That way you can avoid overwriting an existing value.
   See :ref:`Pydantic models` for more information.
