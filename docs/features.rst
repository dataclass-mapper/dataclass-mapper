Supported features
==================

Mapping by field names
----------------------

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
--------------------------

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

Custom conversion functions
---------------------------

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

Recursive models
----------------

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

Here the dataclasses use other dataclasses as fields, either direct ``recipient: Contact`` (and ``recipient: Person``),
or even inside a list ``items: List[OrderItem]`` (and ``items: List[Item]``) or in dictionary values ``items_by_name: dict[str, OrderItem]`` (and ``items_by_name: dict[str, Item]``).
As there is a mapper defined from ``Contact`` to ``Person``, and also a mapper defined from ``OrderItem`` to ``Item``, the object ``custom_order`` can be recusively mapped.

.. warning::
   At the moment it's not possible to create cyclic mappings.

Use default values of the target library
----------------------------------------

Sometimes there is a default value, or default factory in the target class, and you want to use the default value instead of mapping some field from the source class.
This will also use the default in case there is a field with the same name.

.. doctest::
   
   >>> @dataclass
   ... class X:
   ...     x: int = 5
   ...     y: int = field(default_factory=lambda: 42)
   >>>
   >>> @mapper(X, {"x": init_with_default(), "y": init_with_default()})
   ... @dataclass
   ... class Y:
   ...     y: int
   >>>
   >>> map_to(Y(y=0), X)
   X(x=5, y=42)

Optional source fields
----------------------

Optional source fields are handled in a practical way.
The value ``None`` means, that the field is not yet initialized, and if you map the value to a field with a default value, the default value will be taken.

This makes mostly sense, if the default for the target class has a default factory (e.g. like generating a random UUID), and you want to generate a new value if you don't have one yet.

However the result might be a bit surprising.

.. doctest::

   >>> @dataclass
   ... class Target:
   ...     x: int = 5
   ...     y: int = 42
   ...     id: UUID = field(default_factory=uuid4)
   >>>
   >>> @mapper(Target)
   ... @dataclass
   ... class Source:
   ...     x: Optional[int] = None
   ...     y: Optional[int] = None
   ...     id: Optional[UUID] = None
   >>>
   >>> map_to(Source(x=1, y=1, id=UUID('fc22f21a-0720-476f-93d1-1ca67f25a87d')), Target)
   Target(x=1, y=1, id=UUID('fc22f21a-0720-476f-93d1-1ca67f25a87d'))
   >>> map_to(Source(x=2), Target)
   Target(x=2, y=42, id=UUID('38fc07e1-677e-40ef-830c-00e284056dd8'))

It's also possible to map an optional field to a non-optional field, if you can guarantee that the source field is always initialized.

.. doctest::

   >>> @dataclass
   ... class Car:
   ...     value: int
   ...     color: str
   >>>
   >>> @mapper(Car, {"value": assume_not_none("price"), "color": assume_not_none()})
   ... @dataclass
   ... class SportCar:
   ...     price: Optional[int]
   ...     color: Optional[str]
   >>>
   >>> map_to(SportCar(price=30_000, color="red"), Car)
   Car(value=30000, color='red')

.. warning::
   This will not give any warning/exception in case you use it with an object that has `None` values in those fields.

Provide extra context to mapping
--------------------------------

Sometimes you need additional infos for the target object, that you don't have stored in the source class.
With ``provide_with_extra`` you can mark fields, so that no mapping is generated, and the field is filled using an ``extra`` dictionary that can be given to the ``map_to`` function.

.. doctest::

   >>> class TargetItem(BaseModel):
   ...     x: int
   >>>
   >>> @mapper(TargetItem, {"x": provide_with_extra()})
   ... class SourceItem(BaseModel):
   ...     pass
   >>>
   >>> class TargetCollection(BaseModel):
   ...     x: int
   ...     item: TargetItem
   ...     optional_item: Optional[TargetItem]
   ...     items: List[TargetItem]
   >>>
   >>> @mapper(TargetCollection, {"x": provide_with_extra()})
   ... class SourceCollection(BaseModel):
   ...     item: SourceItem
   ...     optional_item: Optional[SourceItem]
   ...     items: List[SourceItem]
   >>>
   >>> source_collection = SourceCollection(
   ...    item=SourceItem(), optional_item=SourceItem(), items=[SourceItem(), SourceItem()]
   ... )
   >>> map_to(
   ...     source_collection,
   ...     TargetCollection,
   ...     extra={"x": 1, "item": {"x": 2}, "optional_item": {"x": 3}, "items": [{"x": 4}, {"x": 5}]}
   ... )
   TargetCollection(x=1, item=TargetItem(x=2), optional_item=TargetItem(x=3), items=[TargetItem(x=4), TargetItem(x=5)])


.. warning::
   Values given via the ``extra`` dictionary are not checked for their correct type.

.. warning::
   When using the ``map_to`` function it is checked, if all the required fields (marked with ``provide_with_extra()``) are given.
   It will raise a ``TypeError`` in case some marked field has no value in the ``extra`` dictionary.

   Use this feature in moderation.
   Forgetting about a value is incredibly easy, especially a nested value, e.g. in a list.
