Potential Ideas
---------------

Pydantic v2 support
===================

Pydantic will release a v2 rewrite soon. They changed quite a bit, so the library will not be compatible as is.

Extra with keys
===============

C#'s Automapper library has a feature, where you can use a key to fill certain fields.
I.e. you mark a field with ``provide_with_extra("age")``, and then pass the value with ``map_to(contact, Person, extra={"age": 42})``.

Check ``Any`` support
=====================

Can the library handle ``Any`` types?

Deep-Copy for nested types
==========================

If there is no conversion necessary, ``dataclass-mapper`` will use shallow-copy for nested structures like lists or recursive objects.
However some use-cases might require copying these structures using deep-copy.
The library `py-automapper <https://github.com/anikolaienko/py-automapper>`_ supports a flag ``deep_copy``.

Overwrite values
================

C#'s Automapper library supports overwriting existing objects.
That's handy if you have an update command, and you just fetch the entity and map the update data onto the entity.
Probably only useful, if we support SqlAlchemy Models first.

Use multiple objects as input
=============================

It might make sense to pass two or more objects as input.
E.g. ``map_to(contact, order, ShippingInfo)``.
It's not clear yet, how the syntax should look like and how it should behave for nested mappings.

Cyclic dependencies
===================

Compile everything, without caring about if functions exist or not.
If they don't exist, just keep a global set of it, and check it if it is possible.

Alternative, expose some lazy mappers:

.. code-block:: python

   from dataclass_mapper.lazy import mapper, compile_mappings

   @mapper(Foo)
   class Bar(BaseModel)
      ...
