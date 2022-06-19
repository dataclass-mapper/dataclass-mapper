import enum
from uuid import UUID

from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base

from safe_mapper.field import MetaField
from safe_mapper.safe_mapper import get_class_fields

Base = declarative_base()


def test_sqlalchemy_normal_field() -> None:
    class MyEnum(enum.Enum):
        one = 1
        two = 2
        three = 3

    class Foo(Base):  # type: ignore
        __tablename__ = "foo"
        x = Column(Integer, primary_key=True, nullable=False)
        y = Column(String(50), nullable=True)
        z = Column(postgresql.UUID)
        a = Column(postgresql.ARRAY(Integer))
        b = Column(Enum(MyEnum))

    fields = get_class_fields(Foo)
    assert fields == {
        "x": MetaField(name="x", type=int, allow_none=False, required=True),
        "y": MetaField(name="y", type=str, allow_none=True, required=True),
        "z": MetaField(name="z", type=UUID, allow_none=True, required=True),
        "a": MetaField(name="a", type=list[int], allow_none=True, required=True),
        "b": MetaField(name="b", type=MyEnum, allow_none=True, required=True),
    }
