Glossary
--------

.. glossary::

   Dataclass
      Classes that are suited for storing data. In our context these should be very simple classes, that have auto-generated initializer methods, and don't dynamically add new fields.

   Field
      A class attribute with type annotation.

   Mapping
      A description of how an object of one class can be transformed into another.
      It describes for each field, how it is filled during the mapping operation.
      E.g. if a field ``Foo.x`` is mapped to a field ``Bar.y``, it describes that the field ``Bar.y`` will be filled with the value of ``Foo.x`` when creating the ``Bar`` object.

   Introspection
      The ability to observe types and properties of objects at runtime.

   Reflection
      Ability to manipulate types, properties, and functions at runtime.
