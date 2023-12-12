.. _OptionalSourceFields:

Optional source fields
----------------------

It's possible to map an optional field to a non-optional field, if you can guarantee that the source field is always initialized.

.. testsetup:: *

   >>> from dataclasses import dataclass, field
   >>> from enum import Enum, auto
   >>> from typing import List, Optional, Dict
   >>> from dataclass_mapper import mapper, map_to, assume_not_none
   >>> from uuid import UUID
   >>> uuid4 = lambda: UUID('38fc07e1-677e-40ef-830c-00e284056dd8')

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

.. note::
   In a previous version (``dataclass-mapper < 1.0.0``) it was also possible to map an optional field to a non-optional target field, if the target field had a default.
   This is no longer possible. If you want to use the default value of a field, use the ``init_with_default`` and ``ignore`` functions.
   See :ref:`Default values handling`.
