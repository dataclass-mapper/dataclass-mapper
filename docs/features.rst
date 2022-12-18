Supported features
==================

Mapping by field names
----------------------

.. testsetup:: *

   >>> from dataclasses import dataclass, field
   >>> from enum import Enum, auto
   >>> from typing import Optional
   >>> from dataclass_mapper import mapper, mapper_from, map_to, enum_mapper, enum_mapper_from, init_with_default, assume_not_none
   >>> from pydantic import BaseModel, Field, validator

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

With the `mapping` parameter it's possible to define how the fields in the target class are filled.
Here we defining a mapper function from the `Contact` class to the `Person` class.
By specifying the mapping `{'"name": "surname"}` (in the order `{"target_field": "source_field"}`) the field `name` in the target class `Person` will be filled with the value of the `surname` of the source class `Contact`.
The `age` will be mapped automatically, as the field name `age` and the type `int` are identically in both classes.
The additional field `first_name` in the `Contact` class will just be ignored.

.. note::
  A mapping is not bidirectional.
  Here you can only map from `Contact` instances to `Person` instances, but not the other way.
  To also have a mapping from `Person` to `Contact`, we would need to add a `@mapper(Contact)` decorator to `Person`, or a `@mapper_from` to `Contact` (see next section).

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

Here we added a decorator `@mapper_from(OrderItem)` to the `Item` class.
That defines a mapper from `OrderItem` instances to `Order` instances.
The order of the mapping parameters is the same, it's `{"target_field": "source_field"}`,
only difference is that the target class is now the class that is decorated.

.. note::
   It's also possible to add multiple decorators to one dataclass.
   E.g. it is possible to add a `mapper` and a `mapper_from` in order to have mappers in both directions.

   .. doctest::

      >>> @mapper(OrderItem, {"name": "description"})
      ... @mapper_from(OrderItem, {"description": "name"})
      ... @dataclass
      ... class Item:
      ...     description: str
      ...     cnt: int

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
The first function `lambda: 45` has no parameters and just returns the constant `45`, so the age will always be initialized with `45`.

In case the function has one parameter, the source object will be passed and you can initialize the field however you want.
In the second function `lambda self: f"{self.first_name} {self.surname}"` there is one parameter `self` (resembling a class method), and it combines the `first_name` and `surname` into a string and initialize the field `name` with it.

.. warning::
   Custom conversion functions are not type-checked.
   So be careful when using them.

Recursive models
----------------

.. doctest::

   >>> @dataclass
   ... class Order:
   ...     recipient: Person
   ...     items: list[Item]
   >>>
   >>> @mapper(Order)
   ... @dataclass
   ... class CustomOrder:
   ...     recipient: Contact
   ...     items: list[OrderItem]
   >>>
   >>> custom_order = CustomOrder(
   ...     recipient=Contact(first_name="Barbara E.", surname="Rolfe"),
   ...     items=[OrderItem(name="fruit", cnt=3), OrderItem(name="sweets", cnt=5)]
   ... )
   >>> map_to(custom_order, Order) #doctest: +NORMALIZE_WHITESPACE
   Order(recipient=Person(name='Barbara E. Rolfe', age=45),
         items=[Item(description='fruit', cnt=3), Item(description='sweets', cnt=5)])

Here the dataclasses use other dataclasses as fields, either direct `recipient: Contact` (and `recipient: Person`),
or even inside a list `items: list[OrderItem]` (and `items: list[Item]`).
As there is a mapper defined from `Contact` to `Person`, and also a mapper defined from `OrderItem` to `Item`, the object `custom_order` can be recusively mapped.

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
The value `None` means, that the field is not yet initialized, and if you map the value to a field with a default value, the default value will be taken.

This makes mostly sense, if the default for the target class is also `None`, or an default factory (e.g. like generating a random UUID).
In case the field in the target class has a different default, the result might be a bit surprising.

.. doctest::

   >>> @dataclass
   ... class Target:
   ...     x1: int = 5
   ...     x2: int = 42
   ...     y1: Optional[int] = None
   ...     y2: Optional[int] = None
   >>>
   >>> @mapper(Target)
   ... @dataclass
   ... class Source:
   ...     x1: Optional[int] = None
   ...     x2: Optional[int] = None
   ...     y1: Optional[int] = None
   ...     y2: Optional[int] = None
   >>>
   >>> map_to(Source(x1=2, y1=1), Target)
   Target(x1=2, x2=42, y1=1, y2=None)

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
