Default values handling
-----------------------

Sometimes there is a default value, or default factory in the target class, and you want to use the default value instead of mapping some field from the source class.
If you mark the field with ``init_with_defaul()`` or with ``ignore()``, it will use the default, even if there is a field with the same name.
The two marks ``init_with_default`` and ``ignore`` are equivalent.

.. testsetup:: *

   >>> from dataclasses import dataclass, field
   >>> from enum import Enum, auto
   >>> from typing import List, Optional, Dict
   >>> from dataclass_mapper import mapper, mapper_from, map_to, enum_mapper, enum_mapper_from, init_with_default, assume_not_none, provide_with_extra, ignore
   >>> from uuid import UUID
   >>> uuid4 = lambda: UUID('38fc07e1-677e-40ef-830c-00e284056dd8')

.. doctest::
   
   >>> @dataclass
   ... class PersonEntity:
   ...     name: str
   ...     age: int
   ...     id: UUID = field(default_factory=uuid4)
   ...     alive: bool = True
   >>>
   >>> @mapper(PersonEntity, {"id": init_with_default(), "alive": ignore()})
   ... @dataclass
   ... class Person:
   ...     id: UUID
   ...     name: str
   ...     age: int
   >>>
   >>> person = Person(name="Jake", age=27, id=UUID("00000000-0000-0000-0000-000000000000"))
   >>> map_to(person, PersonEntity)
   PersonEntity(name='Jake', age=27, id=UUID('38fc07e1-677e-40ef-830c-00e284056dd8'), alive=True)
