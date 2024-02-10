from __future__ import annotations

from typing import List, Optional
from uuid import UUID

import pytest

from dataclass_mapper.classmeta import Namespace, get_class_meta
from dataclass_mapper.fieldtypes import ClassFieldType, ListFieldType, OptionalFieldType
from dataclass_mapper.implementations.sqlalchemy import SQLAlchemyFieldMeta, sqlalchemy_version

if sqlalchemy_version() < (2, 0, 0):
    pytest.skip("Wrong SQLAlchemy Version installed", allow_module_level=True)

from sqlalchemy import ForeignKey, Identity, Integer, String, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.schema import Sequence

empty_namespace = Namespace(locals={}, globals={})


class Base(DeclarativeBase):
    pass


def test_sqlalchemy_normal_field() -> None:
    class Foo(Base):
        __tablename__ = "foo"
        x: Mapped[UUID] = mapped_column(postgresql.UUID, primary_key=True, autoincrement=False)
        y: Mapped[str] = mapped_column(String(64))
        z: Mapped[Optional[int]] = mapped_column(nullable=True)
        a: Mapped[List[int]] = mapped_column(postgresql.ARRAY(Integer))

    fields = get_class_meta(Foo, namespace=empty_namespace).fields
    assert fields == {
        "x": SQLAlchemyFieldMeta(
            attribute_name="x",
            type=ClassFieldType(UUID),
            required=True,
            initializer_param_name="x",
            init_with_ctor=True,
        ),
        "y": SQLAlchemyFieldMeta(
            attribute_name="y", type=ClassFieldType(str), required=True, initializer_param_name="y", init_with_ctor=True
        ),
        "z": SQLAlchemyFieldMeta(
            attribute_name="z",
            type=OptionalFieldType(ClassFieldType(int)),
            required=True,
            initializer_param_name="z",
            init_with_ctor=True,
        ),
        "a": SQLAlchemyFieldMeta(
            attribute_name="a",
            type=ListFieldType(ClassFieldType(int)),
            required=True,
            initializer_param_name="a",
            init_with_ctor=True,
        ),
    }


def test_sqlalchemy_defaults_field() -> None:
    class FooDefaultFields(Base):
        __tablename__ = "foo_default_fields"
        a1: Mapped[int] = mapped_column(primary_key=True)
        a2: Mapped[int] = mapped_column(primary_key=True, autoincrement="auto")
        a3: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
        a4: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
        b1: Mapped[int] = mapped_column(default=lambda: 42)
        b2: Mapped[int] = mapped_column(server_default=text("SELECT 42"))
        b3: Mapped[int] = mapped_column()
        c1: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
        d1: Mapped[int] = mapped_column(Integer, Identity(start=42, cycle=True, always=True))
        d2: Mapped[int] = mapped_column(Integer, Identity(start=42, cycle=True))
        d3: Mapped[int] = mapped_column(Integer, Sequence("d2_seq", start=1))

    fields = get_class_meta(FooDefaultFields, namespace=empty_namespace).fields
    assert not fields["a1"].required
    assert not fields["a2"].required
    assert not fields["a3"].required
    assert fields["a4"].required
    assert not fields["b1"].required
    assert not fields["b2"].required
    assert fields["b3"].required
    assert fields["c1"].required  # actually it's not required, but it also doesn't hurt
    assert not fields["d1"].required
    assert not fields["d2"].required
    assert not fields["d3"].required


def test_sqlalchemy_relationship_field() -> None:
    class Parent(Base):
        __tablename__ = "relationship_parent"
        id: Mapped[int] = mapped_column(primary_key=True)
        children: Mapped[List["Child"]] = relationship(back_populates="parent")

    class Child(Base):
        __tablename__ = "relationship_child"
        id: Mapped[int] = mapped_column(primary_key=True)
        parent_id: Mapped[int] = mapped_column(ForeignKey("relationship_parent.id"))
        parent: Mapped[Parent] = relationship(back_populates="children")

    child_fields = get_class_meta(Child, namespace=empty_namespace).fields
    assert child_fields == {
        "id": SQLAlchemyFieldMeta(
            attribute_name="id",
            type=ClassFieldType(int),
            required=False,
            initializer_param_name="id",
            init_with_ctor=True,
        ),
        "parent_id": SQLAlchemyFieldMeta(
            attribute_name="parent_id",
            type=ClassFieldType(int),
            required=False,
            initializer_param_name="parent_id",
            init_with_ctor=True,
        ),
        "parent": SQLAlchemyFieldMeta(
            attribute_name="parent",
            type=ClassFieldType(Parent),
            required=False,
            initializer_param_name="parent",
            init_with_ctor=True,
        ),
    }

    parents_fields = get_class_meta(Parent, namespace=empty_namespace).fields
    assert parents_fields == {
        "id": SQLAlchemyFieldMeta(
            attribute_name="id",
            type=ClassFieldType(int),
            required=False,
            initializer_param_name="id",
            init_with_ctor=True,
        ),
        "children": SQLAlchemyFieldMeta(
            attribute_name="children",
            type=ListFieldType(ClassFieldType(Child)),
            required=False,
            initializer_param_name="children",
            init_with_ctor=True,
        ),
    }
