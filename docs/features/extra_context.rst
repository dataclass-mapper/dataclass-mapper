Provide extra context to mapping
--------------------------------

Sometimes you need additional infos for the target object, that you don't have stored in the source class.
With ``provide_with_extra`` you can mark fields, so that no mapping is generated, and the field is filled using an ``extra`` dictionary that can be given to the ``map_to`` function.

.. testsetup:: *

   >>> from dataclasses import dataclass, field
   >>> from enum import Enum, auto
   >>> from typing import List, Optional, Dict
   >>> from dataclass_mapper import mapper, mapper_from, map_to, enum_mapper, enum_mapper_from, init_with_default, assume_not_none, provide_with_extra
   >>> from pydantic import BaseModel, Field
   >>> from uuid import UUID
   >>> uuid4 = lambda: UUID('38fc07e1-677e-40ef-830c-00e284056dd8')

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
