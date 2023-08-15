# mypy: disable-error-code="attr-defined"

from typing import Optional, cast
from uuid import UUID, uuid4

import pytest
from sqlalchemy import String
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from dataclass_mapper.implementations.sqlalchemy import sqlalchemy_version
from dataclass_mapper.mapper import map_to, mapper

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
