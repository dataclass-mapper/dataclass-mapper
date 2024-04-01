Simple Type
-----------

It's possible to extract a single value from a dataclass.
And conversly to create a dataclass object from a simple, non-dataclass object, like a string.

E.g. when you work with an ORM, you might have a class like ``TagOrm`` that contains a couple of infos, like the id of the related entity to which the tag belongs to.
However in the API model you only need the name of the tag, so only a single string.

The non-dataclass doesn't have any fields. You can still refer to it with the fieldname ``""``.

Extracting Value
^^^^^^^^^^^^^^^^

For extracting a single value, only the ``CREATE`` mode is possible.


.. testsetup:: *

   >>> from dataclasses import dataclass, field
   >>> from uuid import UUID
   >>> from enum import Enum, auto
   >>> from typing import List, Optional, Dict
   >>> from dataclass_mapper import mapper, mapper_from, map_to, enum_mapper, enum_mapper_from, init_with_default, assume_not_none, ignore, MapperMode, update_only_if_set, create_mapper
   >>> uuid4 = lambda: UUID('38fc07e1-677e-40ef-830c-00e284056dd8')

.. doctest::

   >>> @dataclass
   ... class TagOrm:
   ...     name: str
   ...     entity_id: UUID = field(default_factory=uuid4)
   >>>
   >>> create_mapper(TagOrm, str, {"": "name"}, mapper_mode=MapperMode.CREATE)
   >>> 
   >>> work_tag = TagOrm(name="Work")
   >>> map_to(work_tag, str)
   'Work'

Contructing from Value
^^^^^^^^^^^^^^^^^^^^^^

For extracting a single value, only the ``CREATE`` mode is possible.

.. doctest::

   >>> create_mapper(str, TagOrm, {"name": "", "entity_id": ignore()})
   >>> 
   >>> private_tag = map_to("Private", TagOrm)
   >>> private_tag
   TagOrm(name='Private', entity_id=UUID('38fc07e1-677e-40ef-830c-00e284056dd8'))
   >>>
   >>> map_to("Private/Hobbies", private_tag)
   >>> private_tag
   TagOrm(name='Private/Hobbies', entity_id=UUID('38fc07e1-677e-40ef-830c-00e284056dd8'))
