Introduction and Goals
----------------------

Writing mapper methods between two similar :term:`dataclasses<Dataclass>` in Python is a tedious and error-prone task.
This library ``dataclass-mapper`` should support developers, lighten their workload, and make the program safer.

Requirements Overview
^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :stub-columns: 1

   *  -  Id
      -  Requirement
      -  Explanation

   *  -  F1
      -  Automapping identical fields
      -  Fields with the same name are mapped per default.

   *  -  F2
      -  Configure field mapping
      -  It's possible to specify which source field is mapped to which target field.

   *  -  F3
      -  Recursive mappings
      -  Recursive dataclasses (attributes are other dataclass objects) are mappable to other recursive dataclasses.

   *  -  F4
      -  Configure default values
      -  It's possible to specify which fields are initialized by their default values.

   *  -  F5
      -  Custom mapper functions
      -  It's possible to specify functions that produce the value for the target field.

   *  -  F6
      -  Extra context
      -  It's possible to mark some fields as ``extra`` and provide those infos directly during the mapping operation.

   *  -  F7
      -  Support other dataclasses libraries
      -  It's possible to map between different dataclass implementations (dataclasses, pydantic).

   *  -  F8
      -  Mappings between enum types
      -  It's possible to specify mappings between two enum types.


Types of mapper checks
""""""""""""""""""""""

The following conditions must be checked and guaranteed by the library.
If the mappers are not valid - according to these conditions - a nice exception must be thrown.

.. list-table::
   :header-rows: 1
   :stub-columns: 1

   *  -  Id
      -  Requirement
      -  Explanation

   *  -  C1
      -  Correct field names
      -  All mentioned fields must exist in the corresponding class.

   *  -  C2
      -  Fully initialized
      -  All fields of the target class are initialized after a mapping.

   *  -  C3
      -  Matching types
      -  Source and target fields must have the same types, or are mappable themselves.

Quality Goals
^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :stub-columns: 1

   *  -  Id
      -  Requirement
      -  Explanation

   *  -  Q1
      -  Correct mapper functions
      -  Library creates mappers that successfully convert one dataclass into another.

   *  -  Q2
      -  Type safety
      -  The library guarantees that all field types of the mapped class are according to their dataclass description.

   *  -  Q3
      -  Speed
      -  The generated mapper function should not be slower than a manual written mapper.

   *  -  Q4
      -  Easy syntax
      -  The syntax should be easy understandable, even by people that are not familiar with the library.

   *  -  Q5
      -  Extensible
      -  There are many different dataclass libraries (``dataclasses``, ``pydantic`` v1 and v2, ``attr``, ``sqlalchemy``, ...) with different syntax and features. \
         It should be possible to integrate new dataclass libraries to the ``dataclass-mapper`` library without having to rewrite a lot.


Stakeholders
^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :stub-columns: 1

   *  -  Role/Name
      -  Contact
      -  Expectations

   *  -  Python Software Engineer
      -  using dataclasses
      -  write mapper with less code and in a safer way
