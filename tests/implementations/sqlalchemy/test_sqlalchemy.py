# mypy: disable-error-code="attr-defined,name-defined,misc"

from dataclasses import dataclass
from typing import List, Optional, cast
from uuid import UUID, uuid4

import pytest
from sqlalchemy import Column, ForeignKey, String, Table, create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, joinedload, mapped_column, relationship

from dataclass_mapper import init_with_default
from dataclass_mapper.implementations.sqlalchemy import sqlalchemy_version
from dataclass_mapper.mapper import create_mapper, map_to, mapper, mapper_from

if sqlalchemy_version() < (2, 0, 0):
    pytest.skip("Wrong SQLAlchemy Version installed", allow_module_level=True)


class InMemoryDatabase:
    def __init__(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:", echo=False, future=True)
        self.session = Session(self.engine)

        class Base(DeclarativeBase):
            pass

        self.Base = Base

    def create_all(self) -> None:
        self.Base.metadata.create_all(self.engine)

    def drop_all(self) -> None:
        self.Base.metadata.drop_all(self.engine)


@pytest.fixture()
def db() -> InMemoryDatabase:
    return InMemoryDatabase()


def equal(obj1, obj2) -> bool:
    if type(obj1) != type(obj2):
        return False

    d1 = obj1.__dict__
    d1.pop("_sa_instance_state", None)
    d2 = obj2.__dict__
    d2.pop("_sa_instance_state", None)

    return cast(bool, d1 == d2)


def test_simple_sqlalchemy_mapper(db: InMemoryDatabase):
    class User(db.Base):
        __tablename__ = "user"
        id: Mapped[UUID] = mapped_column(postgresql.UUID, primary_key=True)
        name: Mapped[str] = mapped_column(String(64))
        age: Mapped[Optional[int]] = mapped_column(nullable=True)

    @mapper(User)
    class UserSource(db.Base):
        __tablename__ = "user_source"
        id: Mapped[UUID] = mapped_column(postgresql.UUID, primary_key=True)
        name: Mapped[str] = mapped_column(String(64))
        age: Mapped[Optional[int]] = mapped_column(nullable=True)

    user_id = uuid4()
    user_source = UserSource(id=user_id, name="Test", age=None)
    expected_user = User(id=user_id, name="Test", age=None)
    assert equal(map_to(user_source, User), expected_user)


def test_map_sqlalchemy_relation_to_dataclass(db: InMemoryDatabase):
    class Parent(db.Base):
        __tablename__ = "parent"
        id: Mapped[int] = mapped_column(primary_key=True)

    class Child(db.Base):
        __tablename__ = "child"
        id: Mapped[int] = mapped_column(primary_key=True)
        parent_id: Mapped[int] = mapped_column(ForeignKey("parent.id"))
        parent: Mapped[Parent] = relationship()

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


def test_map_sqlalchemy_relation_from_dataclass_list(db: InMemoryDatabase):
    class Parent(db.Base):
        __tablename__ = "parent"
        id: Mapped[int] = mapped_column(primary_key=True)

    class Child(db.Base):
        __tablename__ = "child"
        id: Mapped[int] = mapped_column(primary_key=True)
        parent_id: Mapped[int] = mapped_column(ForeignKey("parent.id"))
        parent: Mapped[Parent] = relationship()

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


def test_map_sqlalchemy_relation_from_dataclass(db: InMemoryDatabase):
    class ParentTable(db.Base):
        __tablename__ = "parent_table"
        id: Mapped[int] = mapped_column(primary_key=True)
        children: Mapped[List["ChildTable"]] = relationship()

    class ChildTable(db.Base):
        __tablename__ = "child_table"
        id: Mapped[int] = mapped_column(primary_key=True)
        parent_id: Mapped[int] = mapped_column(ForeignKey("parent_table.id"))

    @mapper(ChildTable, {"parent_id": init_with_default()})
    @dataclass
    class ChildDC:
        id: int

    @mapper(ParentTable)
    @dataclass
    class ParentDC:
        id: int
        children: List[ChildDC]

    parent_dc = ParentDC(id=1, children=[ChildDC(id=2), ChildDC(id=3)])
    expected_parent = ParentTable(id=1, children=[ChildTable(id=2), ChildTable(id=3)])
    mapped_parent = map_to(parent_dc, ParentTable)

    assert isinstance(mapped_parent, ParentTable)
    assert mapped_parent.id == expected_parent.id
    assert len(mapped_parent.children) == len(expected_parent.children)
    assert isinstance(mapped_parent.children[0], ChildTable)
    assert mapped_parent.children[0].id == expected_parent.children[0].id
    assert isinstance(mapped_parent.children[1], ChildTable)
    assert mapped_parent.children[1].id == expected_parent.children[1].id


def test_map_sqlalchemy_one_to_many(db: InMemoryDatabase):
    class ParentTable(db.Base):
        __tablename__ = "parent_table"
        id: Mapped[int] = mapped_column(primary_key=True)
        children: Mapped[List["ChildTable"]] = relationship()

    class ChildTable(db.Base):
        __tablename__ = "child_table"
        id: Mapped[int] = mapped_column(primary_key=True)
        parent_id: Mapped[int] = mapped_column(ForeignKey("parent_table.id"))

    @mapper(ChildTable, {"id": init_with_default(), "parent_id": init_with_default()})
    @mapper_from(ChildTable)
    @dataclass
    class Child:
        pass

    @mapper(ParentTable, {"id": init_with_default()})
    @mapper_from(ParentTable)
    @dataclass
    class Parent:
        children: List[Child]

    db.create_all()

    parent = Parent(children=[Child(), Child()])
    parent_entity = map_to(parent, ParentTable)
    db.session.add(parent_entity)
    db.session.commit()

    assert db.session.query(ParentTable).count() == 1
    assert db.session.query(ChildTable).count() == 2

    parent_entity = db.session.query(ParentTable).options(joinedload(ParentTable.children)).one()
    parent = map_to(parent_entity, Parent)

    assert len(parent.children) == 2


def test_map_sqlalchemy_one_to_many_bidirectional(db: InMemoryDatabase):
    class ParentTable(db.Base):
        __tablename__ = "parent_table"
        id: Mapped[int] = mapped_column(primary_key=True)
        children: Mapped[List["ChildTable"]] = relationship(back_populates="parent")

    class ChildTable(db.Base):
        __tablename__ = "child_table"
        id: Mapped[int] = mapped_column(primary_key=True)
        parent_id: Mapped[int] = mapped_column(ForeignKey("parent_table.id"))
        parent: Mapped["ParentTable"] = relationship(back_populates="children")

    @mapper(ChildTable, {"id": init_with_default(), "parent_id": init_with_default(), "parent": init_with_default()})
    @mapper_from(ChildTable)
    @dataclass
    class Child:
        pass

    @mapper(ParentTable, {"id": init_with_default()})
    @mapper_from(ParentTable)
    @dataclass
    class Parent:
        children: List[Child]

    db.create_all()

    parent = Parent(children=[Child(), Child()])
    parent_entity = map_to(parent, ParentTable)
    db.session.add(parent_entity)
    db.session.commit()

    assert db.session.query(ParentTable).count() == 1
    assert db.session.query(ChildTable).count() == 2

    parent_entity = db.session.query(ParentTable).options(joinedload(ParentTable.children)).one()
    parent = map_to(parent_entity, Parent)

    assert len(parent.children) == 2

    @mapper(ParentTable, {"id": init_with_default(), "children": init_with_default()})
    @mapper_from(ParentTable)
    @dataclass
    class Parent2:
        pass

    @mapper(ChildTable, {"id": init_with_default(), "parent_id": init_with_default()})
    @mapper_from(ChildTable)
    @dataclass
    class Child2:
        parent: Parent2

    db.session.query(ChildTable).delete()
    db.session.query(ParentTable).delete()
    db.session.commit()

    child = Child2(parent=Parent2())
    child_entity = map_to(child, ChildTable)
    db.session.add(child_entity)
    db.session.commit()

    assert db.session.query(ParentTable).count() == 1
    assert db.session.query(ChildTable).count() == 1

    child_entity = db.session.query(ChildTable).options(joinedload(ChildTable.parent)).one()
    child = map_to(child_entity, Child2)

    assert child.parent is not None


def test_map_sqlalchemy_many_to_one(db: InMemoryDatabase):
    class ParentTable(db.Base):
        __tablename__ = "parent_table"
        id: Mapped[int] = mapped_column(primary_key=True)
        child_id: Mapped[int] = mapped_column(ForeignKey("child_table.id"))
        child: Mapped["ChildTable"] = relationship()

    class ChildTable(db.Base):
        __tablename__ = "child_table"
        id: Mapped[int] = mapped_column(primary_key=True)

    @mapper(ChildTable, {"id": init_with_default()})
    @mapper_from(ChildTable)
    @dataclass
    class Child:
        pass

    @mapper(ParentTable, {"id": init_with_default(), "child_id": init_with_default()})
    @mapper_from(ParentTable)
    @dataclass
    class Parent:
        child: Child

    db.create_all()

    parent = Parent(child=Child())
    parent_entity = map_to(parent, ParentTable)
    db.session.add(parent_entity)
    db.session.commit()

    assert db.session.query(ChildTable).count() == 1

    parent_entity = db.session.query(ParentTable).one()
    parent = map_to(parent_entity, Parent)
    assert parent.child


def test_map_sqlalchemy_many_to_one_nullable(db: InMemoryDatabase):
    class ParentTable(db.Base):
        __tablename__ = "parent_table"
        id: Mapped[int] = mapped_column(primary_key=True)
        child_id: Mapped[Optional[int]] = mapped_column(ForeignKey("child_table.id"))
        child: Mapped[Optional["ChildTable"]] = relationship(back_populates="parents")

    class ChildTable(db.Base):
        __tablename__ = "child_table"
        id: Mapped[int] = mapped_column(primary_key=True)
        parents: Mapped[List["ParentTable"]] = relationship(back_populates="child")

    @mapper(ChildTable, {"id": init_with_default(), "parents": init_with_default()})
    @mapper_from(ChildTable)
    @dataclass
    class Child:
        pass

    @mapper(ParentTable, {"id": init_with_default(), "child_id": init_with_default()})
    @mapper_from(ParentTable)
    @dataclass
    class Parent:
        child: Optional[Child]

    db.create_all()

    parent1 = Parent(child=None)
    parent1_entity = map_to(parent1, ParentTable)
    parent2 = Parent(child=Child())
    parent2_entity = map_to(parent2, ParentTable)
    db.session.add_all([parent1_entity, parent2_entity])
    db.session.commit()

    assert db.session.query(ChildTable).count() == 1
    assert map_to(db.session.query(ParentTable).where(ParentTable.id == parent1_entity.id).one(), Parent).child is None
    assert (
        map_to(db.session.query(ParentTable).where(ParentTable.id == parent2_entity.id).one(), Parent).child is not None
    )


def test_map_sqlalchemy_one_to_one(db: InMemoryDatabase):
    class ParentTable(db.Base):
        __tablename__ = "parent_table"
        id: Mapped[int] = mapped_column(primary_key=True)
        child: Mapped["ChildTable"] = relationship(back_populates="parent")

    class ChildTable(db.Base):
        __tablename__ = "child_table"
        id: Mapped[int] = mapped_column(primary_key=True)
        parent_id: Mapped[int] = mapped_column(ForeignKey("parent_table.id"))
        parent: Mapped["ParentTable"] = relationship(back_populates="child")

    @mapper(ChildTable, {"id": init_with_default(), "parent_id": init_with_default(), "parent": init_with_default()})
    @mapper_from(ChildTable)
    @dataclass
    class Child:
        pass

    @mapper(ParentTable, {"id": init_with_default()})
    @mapper_from(ParentTable)
    @dataclass
    class Parent:
        child: Child

    db.create_all()

    parent = Parent(child=Child())
    parent_entity = map_to(parent, ParentTable)
    db.session.add(parent_entity)
    db.session.commit()

    assert db.session.query(ChildTable).count() == 1
    assert map_to(db.session.query(ParentTable).one(), Parent).child is not None

    @mapper(ParentTable, {"id": init_with_default(), "child": init_with_default()})
    @mapper_from(ParentTable)
    @dataclass
    class Parent2:
        pass

    @mapper(ChildTable, {"id": init_with_default(), "parent_id": init_with_default()})
    @mapper_from(ChildTable)
    @dataclass
    class Child2:
        parent: Parent2

    child = Child2(parent=Parent2())
    child_entity = map_to(child, ChildTable)
    db.session.add(child_entity)
    db.session.commit()

    assert db.session.query(ParentTable).where(ParentTable.id == child_entity.parent_id).count() == 1
    assert map_to(db.session.query(ChildTable).where(ChildTable.id == child_entity.id).one(), Child2).parent is not None


def test_map_sqlalchemy_many_to_many(db: InMemoryDatabase):
    association_table = Table(
        "association_table",
        db.Base.metadata,
        Column("parent_id", ForeignKey("parent_table.id")),
        Column("child_id", ForeignKey("child_table.id")),
    )

    class ParentTable(db.Base):
        __tablename__ = "parent_table"
        id: Mapped[int] = mapped_column(primary_key=True)
        children: Mapped[List["ChildTable"]] = relationship(secondary=association_table)

    class ChildTable(db.Base):
        __tablename__ = "child_table"
        id: Mapped[int] = mapped_column(primary_key=True)

    @mapper(ChildTable, {"id": init_with_default()})
    @mapper_from(ChildTable)
    @dataclass
    class Child:
        pass

    @mapper(ParentTable, {"id": init_with_default()})
    @mapper_from(ParentTable)
    @dataclass
    class Parent:
        children: List[Child]

    db.create_all()

    child1 = Child()
    child2 = Child()
    parent1 = Parent(children=[child1, child2])

    parent1_entity = map_to(parent1, ParentTable)
    db.session.add(parent1_entity)
    db.session.commit()

    assert db.session.query(ChildTable).count() == 2
    assert db.session.query(ParentTable).count() == 1

    parent2_entity = ParentTable(children=[parent1_entity.children[0]])
    db.session.add(parent2_entity)
    db.session.commit()

    assert db.session.query(ChildTable).count() == 2
    assert db.session.query(ParentTable).count() == 2

    assert (
        len(map_to(db.session.query(ParentTable).where(ParentTable.id == parent2_entity.id).one(), Parent).children)
        == 1
    )


def test_map_sqlalchemy_many_to_many_with_association_object(db: InMemoryDatabase):
    class AssociationTable(db.Base):
        __tablename__ = "association_table"
        left_id: Mapped[int] = mapped_column(ForeignKey("left_table.id"), primary_key=True)
        right_id: Mapped[int] = mapped_column(ForeignKey("right_table.id"), primary_key=True)
        extra_data: Mapped[Optional[str]]
        child: Mapped["ChildTable"] = relationship(viewonly=True)
        parent: Mapped["ParentTable"] = relationship(viewonly=True)

    class ParentTable(db.Base):
        __tablename__ = "left_table"
        id: Mapped[int] = mapped_column(primary_key=True)
        children: Mapped[List["ChildTable"]] = relationship(secondary="association_table", back_populates="parents")

    class ChildTable(db.Base):
        __tablename__ = "right_table"
        id: Mapped[int] = mapped_column(primary_key=True)
        parents: Mapped[List["ParentTable"]] = relationship(secondary="association_table", back_populates="children")

    @mapper(ChildTable, {"id": init_with_default(), "parents": init_with_default()})
    @mapper_from(ChildTable)
    @dataclass
    class Child:
        pass

    @mapper(ParentTable, {"id": init_with_default()})
    @mapper_from(ParentTable)
    @dataclass
    class Parent:
        children: List["Child"]

    db.create_all()

    child1 = Child()
    child2 = Child()
    parent1 = Parent(children=[child1, child2])

    parent1_entity = map_to(parent1, ParentTable)
    child1_entity = parent1_entity.children[0]
    parent2_entity = ParentTable(children=[child1_entity])
    db.session.add_all([parent1_entity, parent2_entity])
    db.session.commit()

    assert db.session.query(ParentTable).count() == 2
    assert db.session.query(ChildTable).count() == 2
    assert db.session.query(AssociationTable).count() == 3

    @mapper_from(ParentTable)
    @dataclass
    class Parent2:
        pass

    @mapper_from(ChildTable)
    @dataclass
    class Child2:
        parents: List["Parent2"]

    child1_entity = db.session.query(ChildTable).where(ChildTable.id == child1_entity.id).one()
    assert len(child1_entity.parents) == 2

    child2_ = map_to(child1_entity, Child2)
    assert len(child2_.parents) == 2


def test_map_sqlalchemy_with_attributes(db: InMemoryDatabase):
    class ParentTargetTable(db.Base):
        __tablename__ = "parent_target_table"
        id: Mapped[int] = mapped_column(primary_key=True)
        children: Mapped[List["ChildTargetTable"]] = relationship()

    class ChildTargetTable(db.Base):
        __tablename__ = "child_target_table"
        id: Mapped[int] = mapped_column(primary_key=True)
        parent_id: Mapped[int] = mapped_column(ForeignKey("parent_target_table.id"))
        name: Mapped[str] = mapped_column(String(64))

    class ParentSourceTable(db.Base):
        __tablename__ = "parent_source_table"
        id: Mapped[int] = mapped_column(primary_key=True)
        children: Mapped[List["ChildSourceTable"]] = relationship()

    class ChildSourceTable(db.Base):
        __tablename__ = "child_source_table"
        id: Mapped[int] = mapped_column(primary_key=True)
        parent_id: Mapped[int] = mapped_column(ForeignKey("parent_source_table.id"))
        child_name: Mapped[str] = mapped_column(String(64))

    with pytest.raises(ValueError) as excinfo:
        create_mapper(
            ChildSourceTable,
            ChildTargetTable,
            {
                ChildSourceTable.id: init_with_default(),
                ChildTargetTable.parent_id: init_with_default(),
                ChildTargetTable.name: ChildSourceTable.child_name,
            },
        )

    assert ("The target field 'id' in the mapping doesn't belong to target class 'ChildTargetTable'.") in str(
        excinfo.value
    )

    with pytest.raises(ValueError) as excinfo:
        create_mapper(
            ChildSourceTable,
            ChildTargetTable,
            {
                ChildTargetTable.id: init_with_default(),
                ChildTargetTable.parent_id: init_with_default(),
                ChildTargetTable.name: ChildTargetTable.name,
            },
        )

    assert ("The source field 'name' in the mapping doesn't belong to source class 'ChildSourceTable'.") in str(
        excinfo.value
    )

    create_mapper(
        ChildSourceTable,
        ChildTargetTable,
        {
            ChildTargetTable.id: init_with_default(),
            ChildTargetTable.parent_id: init_with_default(),
            ChildTargetTable.name: ChildSourceTable.child_name,
        },
    )
    create_mapper(ParentSourceTable, ParentTargetTable, {ParentTargetTable.id: init_with_default()})
