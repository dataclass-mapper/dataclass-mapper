# mypy: disable-error-code="attr-defined"

from dataclasses import dataclass
from typing import Optional, cast
from uuid import UUID, uuid4

import pytest
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from dataclass_mapper import init_with_default
from dataclass_mapper.implementations.sqlalchemy import sqlalchemy_version
from dataclass_mapper.mapper import map_to, mapper, mapper_from

if sqlalchemy_version() < (2, 0, 0):
    pytest.skip("Wrong SQLAlchemy Version installed", allow_module_level=True)


class Base(DeclarativeBase):
    pass


def equal(obj1, obj2) -> bool:
    if type(obj1) != type(obj2):
        return False

    d1 = obj1.__dict__
    d1.pop("_sa_instance_state", None)
    d2 = obj2.__dict__
    d2.pop("_sa_instance_state", None)

    return cast(bool, d1 == d2)


class User(Base):
    __tablename__ = "user"
    id: Mapped[UUID] = mapped_column(postgresql.UUID, primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    age: Mapped[Optional[int]] = mapped_column(nullable=True)


def test_simple_sqlalchemy_mapper():
    @mapper(User)
    class UserSource(Base):
        __tablename__ = "user_source"
        id: Mapped[UUID] = mapped_column(postgresql.UUID, primary_key=True)
        name: Mapped[str] = mapped_column(String(64))
        age: Mapped[Optional[int]] = mapped_column(nullable=True)

    user_id = uuid4()
    user_source = UserSource(id=user_id, name="Test", age=None)
    expected_user = User(id=user_id, name="Test", age=None)
    assert equal(map_to(user_source, User), expected_user)


class Parent(Base):
    __tablename__ = "parent"
    id: Mapped[int] = mapped_column(primary_key=True)


class Child(Base):
    __tablename__ = "child"
    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("parent.id"))
    parent: Mapped[Parent] = relationship()


def test_map_sqlalchemy_relation_to_dataclass():
    @mapper_from(Parent)
    @dataclass
    class ParentDC:
        id: int

    @mapper_from(Child)
    @dataclass
    class ChildDC:
        id: int
        parent: ParentDC

    child = Child(id=1, parent=Parent(id=2))
    expected_child_dc = ChildDC(id=1, parent=ParentDC(id=2))
    assert map_to(child, ChildDC) == expected_child_dc


def test_map_sqlalchemy_relation_from_dataclass():
    @mapper(Parent)
    @dataclass
    class ParentDC:
        id: int

    @mapper(Child, {"parent_id": init_with_default()})
    @dataclass
    class ChildDC:
        id: int
        parent: ParentDC

    child_dc = ChildDC(id=1, parent=ParentDC(id=2))
    expected_child = Child(id=1, parent=Parent(id=2))
    mapped_child = map_to(child_dc, Child)

    assert isinstance(mapped_child, Child)
    assert mapped_child.id == expected_child.id
    assert isinstance(mapped_child.parent, Parent)
    assert mapped_child.parent.id == expected_child.parent.id
