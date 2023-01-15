Enum mappings
=============

.. testsetup:: *

   >>> from dataclasses import dataclass, field
   >>> from enum import Enum, auto
   >>> from typing import Optional
   >>> from dataclass_mapper import mapper, mapper_from, map_to, enum_mapper, enum_mapper_from, init_with_default, assume_not_none
   >>> from pydantic import BaseModel, Field, validator

.. doctest::

   >>> class ProgrammingLanguage(Enum):
   ...     PYTHON = auto()
   ...     JAVA = auto()
   ...     CPLUSPLUS = auto()
   >>>
   >>> @enum_mapper(ProgrammingLanguage, {"PY": "PYTHON", "CPP": "CPLUSPLUS", "H": "CPLUSPLUS"})
   ... class FileEndings(str, Enum):
   ...    PY = ".py"
   ...    JAVA = ".java"
   ...    CPP = ".cpp"
   ...    H = ".h"
   >>>
   >>> map_to(FileEndings.PY, ProgrammingLanguage)
   <ProgrammingLanguage.PYTHON: 1>


Here a mapping between two enums is defined.
Notice, that the order of the mapping is defined in the opposite way.
For each member of the source enum, you have to list the member of the target enum.
That way you can also map multiple source members to the same target member.
In the example both ``FileEndings.CPP`` and ``FileEndings.H`` are mapped to ``ProgrammingLanguage.CPLUSPLUS``.

As always, if enum members have the same name, you don't need specify them in the mapping.
And it's also possible to define a member to the current class with ``enum_mapper_from``.

.. note::
   It's also possible to specify the target members directly instead of strings.

   .. doctest::

      >>> @enum_mapper(
      ...     ProgrammingLanguage,
      ...     {
      ...         "PY": ProgrammingLanguage.PYTHON,
      ...         "CPP": ProgrammingLanguage.CPLUSPLUS,
      ...         "H": ProgrammingLanguage.CPLUSPLUS
      ...     }
      ... )
      ... class FileEndings(str, Enum):
      ...    PY = ".py"
      ...    JAVA = ".java"
      ...    CPP = ".cpp"
      ...    H = ".h"

   For the source class ``FileEndings`` that's not possible, because the ``FileEndings`` class doesn't exist yet for the decorator.
