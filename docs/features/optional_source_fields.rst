Optional source fields
----------------------

Optional source fields are handled in a practical way.
The value ``None`` means, that the field is not yet initialized, and if you map the value to a field with a default value, the default value will be taken.

This makes mostly sense, if the default for the target class has a default factory (e.g. like generating a random UUID), and you want to generate a new value if you don't have one yet.

However the result might be a bit surprising.

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
