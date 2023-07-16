Solution Strategy
-----------------

.. list-table::
   :header-rows: 1

   *  -  Goal/Requirement
      -  Solution approach

   *  -  Generating mappers should only be possible if it's guaranteed that the mapped object will be valid (**Safety**)
      -  Use Python's :term:`introspection` capabilities to analyze all fields in both classes, \
         check if all fields can be matched and if the types of the fields are compatible. \
         See :ref:`Introspection`

   *  -  Running a generated mapper should not be slower than running a handwritten mapper (**Speed**)
      -  Use :term:`reflection` (e.g. `exec`) to generate a fast conversion function that's equivalent to a handwritten mapper function. \
         All checks (see the safety requirement) will be done only once - while defining the mapper - but not every single time \
         when the mapper is run.
         See :ref:`Mapper Function Generation`

   *  -  Integrating new dataclass libraries should be easy (**Extensible**)
      -  Use the strategy pattern to define a class (*strategy*) for each dataclass implementation. \
         Each class will have a method to check if a given class is supported by it, and provides methods of extracting information about the class and the fields in a uniform way.
         All the other mapping logic is decoupled from the implementation specific logic.
