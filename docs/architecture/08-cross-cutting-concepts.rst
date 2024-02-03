Cross-cutting Concepts
----------------------

Introspection
^^^^^^^^^^^^^

Most dataclass implementations have an easy way to accessing the list of their fields and their types. For example, the ``dataclasses`` module provides the ``dataclasses.fields(class)`` method, or the ``Pydantic`` library exposes the ``__fields__`` class attribute.
This allows fetching all fields for the source class and the target class already when the mapper is defined, and perform all kinds o[] checks on the fields.

It's possible to check if all the fields will be filled, and also possible to compare the types of the fields.

These checks eliminate the need to perform them when mapping an actual object.

However, we assume that the given object satisfies the dataclass definition (which is not guaranteed due to dynamic typing).
If the object has attributes with incorrect types, our library will generate a mapped object with incorrect types as well.
In such a case, there is limited action we can take in any way.
If developers care about their types (which they should), they can use a static type checker like `mypy <https://mypy-lang.org/>`_.
By doing so, the object will fulfill the dataclass definition, and our library will ensure a valid mapped instance without runtime field and type checks.

Converting string type annotations to types
"""""""""""""""""""""""""""""""""""""""""""

It's quite common that types are specified as strings.
Sometimes that's even required (e.g. for models with circular dependencies) or when you use ``from __future__ import annotations``.

.. code-block:: python

   @dataclass
   class Contact:
       name: "str"
       address: "Address"

Pydantic automatically determines the types, but ``dataclasses`` just track them as strings.

It's possible to still extract the correct type in such a case with the ``typing.get_type_hints`` method.
It is a bit difficult to use though, as you need to provide the local and global namespaces, in which those types are defined.
These are - typically - the namespaces at the location of the class definition.
If not, then also tools like ``mypy`` will complain about not understanding the 

If the decorator ``@mapper(TargetCls)`` is used, the required namespace can be extracted via the call stack.

.. code-block:: python

   def mapper(target_cls):
       frame = sys._getframe(depth=1)
       localns = frame.f_locals
       globalns = frame.f_globals
       real_types = get_type_hints(target_cls, globalns=globalns, localns=localns)

Mapper Function Generation
^^^^^^^^^^^^^^^^^^^^^^^^^^

From the :ref:`Introspection` we receive a list of fields and can determine how a mapping will work.
We create a mapper function that performs the mapping as a string.
E.g. for two given classes ``Foo`` and ``Bar`` - one with a field ``x`` and one with a field ``y`` of the same type - an AST (abstract syntax tree) will be generated, that's more or less equivalent to the following code snippet.

.. code-block:: python

   function = """
   def convert(self, source: Foo) -> Bar:
       d = {}
       d["y"] = source.x
       return Bar(**d)
   """

This function as code will afterwards executed, to make the function available to use whenever you want to convert an object.

This approach has the advantage, that a mapping operation no longer has to do any hard tasks any more.
It's no longer necessary to get the list of fields of both classes, it's no longer to check the types, etc.

This expected speedup gains have not been evaluated before implementing this approach, but retroactively we performed a small benchmark and compared the ``dataclass-mapper`` library with the `py-automapper <https://github.com/anikolaienko/py-automapper>`_ library. That library doesn't use reflection.
While mapping an object, they fetch a list of fields of the target class, iterate over them, look up for each field how they should fill a field, etc.

For the small example given below, the ``py-automapper`` library (release 1.2.3) needed about ~4.19 μs to convert an instance of type ``User`` to an instance of type ``Person``, while the ``dataclass-mapper`` library (release 1.7.2) took ~1.22 μs.

.. code-block:: python

   @dataclass
   class User:
       name: str
       username: str
       age: int

   @dataclass
   class Person:
       name: str
       age: int
