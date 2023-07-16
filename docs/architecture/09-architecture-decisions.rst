Architecture Decisions
----------------------

.. toctree::
   :maxdepth: 1
   :glob:

   adr/*

.. ADR 10: Disallow mapping optional types
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. In version ``v1.x.y`` it was allowed to map an ``Optional[T]`` to an ``T`` field, if the target field had a default value.
.. The reason behind this was, that it's quite common to give fields in a class the default value ``Null`` or define a factory for them (e.g. generating a UUID).
.. However that complicated the full logic of the mappers, while we are defining them, using them, and also the code of the library itself gets really complicated.

.. For version ``v2.0.0`` this will be disallowed.

.. TODO: ^ null doesn't actually make any sense, as the target is non-optional.
.. The error also appears in the current docs.

.. Possible fixes:

.. .. code-block:: python

..    class Bar(BaseModel):
..       y: int = Field(default_factory=uuid.uuid4)

..    @mapper(Bar, {"y": use_default_if_null("x")})
..    class Foo(BaseModel):
..        x: Optional[int]

.. or use the already existing ``init_with_default()``.
