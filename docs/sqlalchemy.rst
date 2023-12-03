SQLAlchemy ORM models
=====================

The library can also handle (some) SQLAlchemy's ORM models, and map to them and from them.

.. warning::
   SQLAlchemy is a pretty big library.
   The basic things work, although there might be advanced features that are not supported as of now.

At the moment it has support for:

* Default SQLAlchemy Types (``BigInteger``, ``Boolean``, ``Date``, ``DateTime``, ``Float``,
  ``Integer``, ``Interval``, ``LargeBinary``, ``SmallInteger``,
  ``String``, ``Text``, ``Time``, ``Unicode``, ``UnicodeText``)
* Enums (``Enum(MyEnumType)``)
* Some PostgreSQL specific types: (``UUID``, ``ARRAY``)
* Relationships (1:n, n:1, 1:1, n:n)
* Association Objects

Mapping from ORM models
-----------------------

.. testsetup:: *

   >>> import pytest
   >>> from dataclass_mapper.implementations.sqlalchemy import sqlalchemy_version
   >>> if sqlalchemy_version() < (2, 0, 0):
   ...     pytest.skip("Wrong SQLAlchemy Version installed", allow_module_level=True)
   >>> from dataclasses import dataclass
   >>> from datetime import date
   >>> from typing import List, Optional
   >>>
   >>> from sqlalchemy import Date, ForeignKey, SmallInteger, String, create_engine
   >>> from sqlalchemy.orm import DeclarativeBase, Mapped, Session, joinedload, mapped_column, relationship
   >>>
   >>> from dataclass_mapper import map_to, mapper, mapper_from, init_with_default, ignore, MapperMode
   >>>
   >>> engine = create_engine("sqlite+pysqlite:///:memory:", echo=False, future=True)
   >>> session = Session(engine)
   >>>
   >>> class Base(DeclarativeBase):
   ...     pass


Here's a short example.
Two tables - a parent table and a child table - with with one relationship - a parent can have multiple children, but every child has exactly one parent.

.. doctest::

   >>> class ChildORM(Base):
   ...     __tablename__ = "child"
   ...     id: Mapped[int] = mapped_column(primary_key=True)
   ...     name: Mapped[str] = mapped_column(String(64))
   ...     date_of_birth: Mapped[date] = mapped_column(Date)
   ...     parent_id: Mapped[int] = mapped_column(ForeignKey("parent.id"))
   >>>
   >>> class ParentORM(Base):
   ...     __tablename__ = "parent"
   ...     id: Mapped[int] = mapped_column(primary_key=True)
   ...     name: Mapped[str] = mapped_column(String(64))
   ...     age: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
   ...     children: Mapped[List[ChildORM]] = relationship()

.. testsetup:: *

   >>> Base.metadata.create_all(engine)
   >>> c1 = ChildORM(name="Alice", date_of_birth=date(year=2000, month=2, day=15))
   >>> c2 = ChildORM(name="Bob", date_of_birth=date(year=2002, month=5, day=3))
   >>> p = ParentORM(name="Frank", age=45, children=[c1, c2])
   >>> session.add(p)
   >>> session.commit()

Also we the following two dataclasses:

.. doctest::

   >>> @mapper_from(ChildORM)
   ... @dataclass
   ... class Child:
   ...     name: str
   ...     date_of_birth: date
   >>>
   >>> @mapper_from(ParentORM)
   ... @dataclass
   ... class Parent:
   ...     name: str
   ...     age: Optional[int]
   ...     children: List[Child]

If we now query the database, we can map the result to the dataclass models.

.. doctest::

   >>> parent_orm = session.query(ParentORM).options(joinedload(ParentORM.children)).one()
   >>> map_to(parent_orm, Parent) #doctest: +NORMALIZE_WHITESPACE
   Parent(name='Frank', age=45,
          children=[Child(name='Alice', date_of_birth=datetime.date(2000, 2, 15)),
                    Child(name='Bob', date_of_birth=datetime.date(2002, 5, 3))])

Mapping to ORM models
---------------------

If you do it the other way round, you might need to ignore the occasional primary key or foreign key fields.

.. doctest::

   >>> @mapper(ChildORM, {"parent_id": ignore(), "id": ignore()})
   ... @dataclass
   ... class CreateChild:
   ...     name: str
   ...     date_of_birth: date
   >>>
   >>> @mapper(ParentORM, {"id": ignore()})
   ... @dataclass
   ... class CreateParent:
   ...     name: str
   ...     age: Optional[int]
   ...     children: List[CreateChild]
   >>>
   >>> new_child = CreateChild(name="Amelia", date_of_birth=date(2023, 10, 14))
   >>> new_parent = CreateParent(name="Emma", age=33, children=[new_child])
   >>> parent_orm = map_to(new_parent, ParentORM)
   >>> session.add(parent_orm)
   >>> session.commit()
   >>>
   >>> session.query(ChildORM).where(ChildORM.name == "Amelia").one().date_of_birth
   datetime.date(2023, 10, 14)

As with other classes, you can update existing models.

.. doctest::

   >>> @mapper(ParentORM, {"id": ignore(), "name": ignore(), "children": ignore()}, mapper_mode=MapperMode.UPDATE)
   ... @dataclass
   ... class ParentUpdate:
   ...     age: int
   >>>
   >>> parent_update = ParentUpdate(age=34)
   >>> map_to(parent_update, parent_orm)
   >>> session.commit()
   >>>
   >>> session.query(ParentORM).where(ParentORM.name == "Emma").one().age
   34

Mapping using ORM attributes
----------------------------

In SQLAlchemy the specified columns and relationships are also class attributes (e.g. in order to use them for querying).
That also allows us to use them when you specify mappings, and you don't need to rely on strings.

This is not possible with ``dataclasses`` or ``pydantic``.

.. doctest::

   >>> @mapper(ChildORM, {ChildORM.parent_id: ignore(), ChildORM.id: ignore()})
   ... @dataclass
   ... class CreateChild:
   ...     name: str
   ...     date_of_birth: date
