Define mappings
---------------

Define a basic mapping
^^^^^^^^^^^^^^^^^^^^^^

You can define a new mapping using the :func:`~dataclass_mapper.create_mapper` function.

.. testsetup:: *

   >>> from dataclasses import dataclass, field
   >>> from enum import Enum, auto
   >>> from typing import List, Optional, Dict
   >>> from dataclass_mapper import mapper, mapper_from, map_to, enum_mapper, enum_mapper_from, init_with_default, assume_not_none, create_mapper, MapperMode

.. doctest::

   >>> @dataclass
   ... class Person:
   ...     name: str
   ...     age: int
   >>>
   >>> @dataclass
   ... class Contact:
   ...     name: str
   ...     age: int
   >>>
   >>> create_mapper(Contact, Person)
   >>>
   >>> contact = Contact(name="Jesse Cross", age=50)
   >>> map_to(contact, Person)
   Person(name='Jesse Cross', age=50)

Here we defining a mapper function from the ``Contact`` class to the `Person` class.
The library will analyze both dataclasses and their fields, and will create mapper function(s) that you can use use later to convert / overwrite an object using :func:`~dataclass_mapper.map_to`.
Fields with the same name and type are mapped automatically.

.. doctest::

   >>> contact = Contact(name="Jesse Cross", age=50)
   >>> map_to(contact, Person)
   Person(name='Jesse Cross', age=50)

.. note::
   A mapping is not bidirectional.
   Here you can only map from ``Contact`` instances to ``Person`` instances, but not the other way.
   To also have a mapping from ``Person`` to ``Contact``, we would need to create another mapping from ``Person`` to ``Contact``.

.. note::
   It is checked if the types of the fields are compatible, i.e. if the target field allows all the type options of the source field.
   E.g. it is allowed to map from a ``str`` field to a ``Union[str, int]`` field or to an ``Optional[str]`` field, but not the other way around.
   Although you can loosen up those checks or disable them with the methods described in :ref:`OptionalSourceFields` and :ref:`CustomConversionFunctions`.

Define mappings via decorators
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Instead of using the :func:`~dataclass_mapper.create_mapper` function, you can also use the :func:`~dataclass_mapper.mapper` and :func:`~dataclass_mapper.mapper_from` decorators as shortcuts.
They take the same parameters, and are equivalent to the :func:`~dataclass_mapper.create_mapper` function.

With :func:`~dataclass_mapper.mapper` you define a mapping from the current class to the specified class.

.. doctest::

   >>> @mapper(Person)
   ... @dataclass
   ... class Contact:
   ...     name: str
   ...     age: int
   >>>
   >>> contact = Contact(name="Jesse Cross", age=50)
   >>> map_to(contact, Person)
   Person(name='Jesse Cross', age=50)

With :func:`~dataclass_mapper.mapper_from` you define a mapping from the passed class to the current class.

.. doctest::

   >>> @mapper_from(Person)
   ... @dataclass
   ... class Contact:
   ...     name: str
   ...     age: int
   >>>
   >>> person = Person(name="Jesse Cross", age=50)
   >>> map_to(person, Contact)
   Contact(name='Jesse Cross', age=50)
   
.. note::
   It's also possible to add multiple decorators to one dataclass.
   E.g. it is possible to add a ``mapper`` and a ``mapper_from`` in order to have mappers in both directions, or even create mappings to/from multiple classes.

Mapper mode
^^^^^^^^^^^

The functions :func:`~dataclass_mapper.create_mapper`, :func:`~dataclass_mapper.mapper`, and :func:`~dataclass_mapper.mapper_from` take an optional parameter, the mapper mode.
Per default it has the value :py:enum:mem:`~dataclass_mapper.MapperMethod.CREATE_AND_UPDATE`.
That means it will both create a mapper for creating new target objects from the source object, but also a mapper for updating existing target objects.
The 

.. doctest::

   >>> person = Person(name="Jesse Cross", age=50)
   >>> contact = Contact(name="No Name", age=0)
   >>> map_to(person, contact)
   >>> contact
   Contact(name='Jesse Cross', age=50)

The ``contact`` object is still the same one (it has the same ``id`` as before).
See :ref:`Update models` for more information about updating existing target objects.

In general it is best practice to only define the mappers that you really need, in order to avoid that somebody uses the mapper in an unintended way.
E.g. you can limit the mapper to only creating new objects with the following:

.. testsetup:: *

   >>> # redefine the class, in order to delete the old mapper definitions
   >>> @dataclass
   ... class Person:
   ...     name: str
   ...     age: int

.. doctest::

   >>> @mapper_from(Person, mapper_mode=MapperMode.CREATE)
   ... @dataclass
   ... class Contact:
   ...     name: str
   ...     age: int
   >>>
   >>> person = Person(name="Jesse Cross", age=50)
   >>>
   >>> # creating a new object works
   >>> map_to(person, Contact)
   Contact(name='Jesse Cross', age=50)
   >>>
   >>> # attempting to update an existing object fails (which would work otherwise).
   >>> contact = Contact(name="No Name", age=0)
   >>> map_to(person, contact)
   Traceback (most recent call last):
      ...
   NotImplementedError: Object of type 'Person' cannot be mapped to 'Contact'
