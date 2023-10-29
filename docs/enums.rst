Enum mappings
=============

Define Enum mappings
--------------------

You can define a mapping between two Enum classes using the :func:`~dataclass_mapper.create_enum_mapper` function.

.. testsetup:: *

   >>> from dataclasses import dataclass, field
   >>> from enum import Enum, auto
   >>> from typing import Optional
   >>> from dataclass_mapper import mapper, mapper_from, map_to, enum_mapper, enum_mapper_from, init_with_default, assume_not_none, create_enum_mapper

.. doctest::

   >>> class ProgrammingLanguage(Enum):
   ...     PYTHON = auto()
   ...     JAVA = auto()
   ...     CPLUSPLUS = auto()
   >>>
   >>> class FileEndings(str, Enum):
   ...    PY = ".py"
   ...    JAVA = ".java"
   ...    CPP = ".cpp"
   ...    H = ".h"
   >>>
   >>> create_enum_mapper(FileEndings, ProgrammingLanguage,
   ...     {
   ...         FileEndings.PY: ProgrammingLanguage.PYTHON,
   ...         FileEndings.CPP: ProgrammingLanguage.CPLUSPLUS,
   ...         FileEndings.H: ProgrammingLanguage.CPLUSPLUS
   ...     }
   ... )

Here a mapping from the enum ``FileEndings`` to the enum ``ProgrammingLanguage`` is defined.

Notice, that the order of the mapping is defined in the opposite way in comparison to the dataclass mappers.
For each member of the source enum, you have to list the member of the target enum.
That way you can also map multiple source members to the same target member.
In the example both ``FileEndings.CPP`` and ``FileEndings.H`` are mapped to ``ProgrammingLanguage.CPLUSPLUS``.

The library will analyze both enums, and will create a mapper function(s) that you can use use later to convert / overwrite an object using the typical :func:`~dataclass_mapper.map_to` function.

.. doctest::

   >>> map_to(FileEndings.PY, ProgrammingLanguage)
   <ProgrammingLanguage.PYTHON: 1>

It's also possible to specify the target members as strings instead of the actual values.

.. testsetup::

   >>> class FileEndings(str, Enum):
   ...    PY = ".py"
   ...    JAVA = ".java"
   ...    CPP = ".cpp"
   ...    H = ".h"

.. doctest::

   >>> create_enum_mapper(FileEndings, ProgrammingLanguage, {"PY": "PYTHON", "CPP": "CPLUSPLUS", "H": "CPLUSPLUS"})
   >>>
   >>> map_to(FileEndings.PY, ProgrammingLanguage)
   <ProgrammingLanguage.PYTHON: 1>

As always, if enum members have the same name, you don't need specify them in the mapping.
And the library will make sure, that you don't forget any enum values.

Define enum mappings via decorators
-----------------------------------

Instead of using the :func:`~dataclass_mapper.create_enum_mapper` function, you can also use the :func:`~dataclass_mapper.enum_mapper` and :func:`~dataclass_mapper.enum_mapper_from` decorators as shortcuts.
They take the same parameters, and are equivalent to the :func:`~dataclass_mapper.create_enum_mapper` function.

You will however have to use strings for the fields of the current class, because Python doesn't know about them yet.
However be assured, that the library will warn you when you misspell or forget some fields.

.. doctest::

   >>> @enum_mapper(ProgrammingLanguage, {"PY": ProgrammingLanguage.PYTHON, "CPP": ProgrammingLanguage.CPLUSPLUS, "H": ProgrammingLanguage.CPLUSPLUS})
   ... class FileEndings(str, Enum):
   ...    PY = ".py"
   ...    JAVA = ".java"
   ...    CPP = ".cpp"
   ...    H = ".h"
   >>>
   >>> map_to(FileEndings.PY, ProgrammingLanguage)
   <ProgrammingLanguage.PYTHON: 1>

.. testsetup::

   >>> class FileEndings(str, Enum):
   ...    PY = ".py"
   ...    JAVA = ".java"
   ...    CPP = ".cpp"
   ...    H = ".h"

.. doctest::

   >>> @enum_mapper_from(FileEndings, {FileEndings.PY: "PYTHON", FileEndings.CPP: "CPLUSPLUS", FileEndings.H: "CPLUSPLUS"})
   ... class ProgrammingLanguage(Enum):
   ...     PYTHON = auto()
   ...     JAVA = auto()
   ...     CPLUSPLUS = auto()
   >>>
   >>> map_to(FileEndings.PY, ProgrammingLanguage)
   <ProgrammingLanguage.PYTHON: 1>
