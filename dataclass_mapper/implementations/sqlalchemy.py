from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, cast
from uuid import UUID

from dataclass_mapper.implementations.utils import parse_version
from dataclass_mapper.namespace import Namespace

from .base import ClassMeta, DataclassType, FieldMeta


def sqlalchemy_version() -> Tuple[int, int, int]:
    sqlalchemy = __import__("sqlalchemy")
    return parse_version(cast(str, sqlalchemy.__version__))


@dataclass
class SQLAlchemyFieldMeta(FieldMeta):
    # for relationships
    paired_relationship_field: Optional[str] = None

    @classmethod
    def from_sqlalchemy(cls, field: Any, name: str) -> "SQLAlchemyFieldMeta":
        # TODO: disable "GENERATED ALWAYS columns" (e.g. Column(Identity(always=True)))
        return cls(
            name=name,
            type=cls._extract_sqlalchemy_type(field.type),
            allow_none=field.nullable,
            required=cls._is_required(field),
            alias=None,
        )

    @classmethod
    def _extract_sqlalchemy_type(cls, type_):
        sqlalchemy = __import__("sqlalchemy")
        psql = __import__("sqlalchemy.dialects.postgresql")

        if isinstance(type_, psql.ARRAY):
            item_type = cls._extract_sqlalchemy_type(type_.item_type)
            return List[item_type]  # type: ignore[valid-type]

        if isinstance(type_, sqlalchemy.Enum):
            return type_.enum_class

        type_mapping = {
            sqlalchemy.BigInteger: int,
            sqlalchemy.Boolean: bool,
            sqlalchemy.Date: date,
            sqlalchemy.DateTime: datetime,
            sqlalchemy.Float: float,
            sqlalchemy.Integer: int,
            sqlalchemy.Interval: timedelta,
            sqlalchemy.LargeBinary: bytes,
            sqlalchemy.SmallInteger: int,
            sqlalchemy.String: str,
            sqlalchemy.Text: str,
            sqlalchemy.Time: time,
            sqlalchemy.Unicode: str,
            sqlalchemy.UnicodeText: str,
            psql.UUID: UUID,
        }

        for sqlalchemy_cls, mapped_type in type_mapping.items():
            if isinstance(type_, sqlalchemy_cls):
                return mapped_type

        raise NotImplementedError(f"type '{type_}' is not supported")

    @staticmethod
    def _is_required(field: Any) -> bool:
        if field.default is not None or field.server_default is not None:
            return False
        if field.primary_key and field.autoincrement in ("auto", True):
            return False

        return True


class SQLAlchemyClassMeta(ClassMeta):
    _type = DataclassType.PYDANTIC

    def __init__(
        self,
        name: str,
        fields: Dict[str, FieldMeta],
        alias_name: Optional[str] = None,
    ) -> None:
        super().__init__(name=name, fields=fields, alias_name=alias_name)

    def get_assignment_name(self, field: FieldMeta) -> str:
        return field.name

    @staticmethod
    def _fields(clazz: Any, namespace: Namespace) -> Dict[str, SQLAlchemyFieldMeta]:
        sqlalchemy = __import__("sqlalchemy")
        return {
            field.name: SQLAlchemyFieldMeta.from_sqlalchemy(field, field.name)
            for field in sqlalchemy.inspect(clazz).columns
        }

    @staticmethod
    def _relationship_fields(
        clazz: Any, column_fields: dict[str, SQLAlchemyFieldMeta], namespace: Namespace
    ) -> Dict[str, FieldMeta]:
        sqlalchemy = __import__("sqlalchemy")
        fields: Dict[str, FieldMeta] = {}
        for relationship in sqlalchemy.inspect(clazz).relationships:
            type_ = relationship.mapper.class_
            if relationship.collection_class is list:
                type_ = List[type_]  # type: ignore[valid-type]
            if relationship.collection_class is set:
                type_ = Set[type_]  # type: ignore[valid-type]
            name = relationship._dependency_processor.key

            # For a 1:n relationship, both entities can have the relationship property.
            # A relationship depends of 2 ids that are linked, usually one primary key and one foreign key.
            # The child entity has the MANYTOONE direction, and one column that marks the foreign key.
            # The parent entity has the ONETOMANY direction, and the local column of the relationship is
            # it's own primary key.
            paired_relationship_field = None
            if relationship.direction == sqlalchemy.orm.RelationshipDirection.MANYTOONE and relationship.local_columns:
                if len(relationship.local_columns) > 1:
                    raise NotImplementedError("Not supported case, SQLAlchemy relationship has multiple local columns")
                paired_relationship_field = list(relationship.local_columns)[0].name

                # also adjust the foreign key field
                column_fields[paired_relationship_field].paired_relationship_field = name

            fields[name] = SQLAlchemyFieldMeta(
                name=name,
                type=type_,
                allow_none=False,  # TODO: is this always the case?
                required=False,  # TODO: is this always the case?
                paired_relationship_field=paired_relationship_field,
            )
            # todo: what if `relationship(viewonly=True)` is set?
        return fields

    @staticmethod
    def applies(clz: Any) -> bool:
        try:
            sqlalchemy = __import__("sqlalchemy")
            try:
                sqlalchemy.inspect(clz)
                return (2, 0, 0) <= sqlalchemy_version() < (3, 0, 0)
            except sqlalchemy.exc.NoInspectionAvailable:
                pass
        except ImportError:
            pass
        return False

    @classmethod
    def from_clazz(cls, clazz: Any, namespace: Namespace) -> "SQLAlchemyClassMeta":
        column_fields = cls._fields(clazz, namespace=namespace)
        relationship_fields = cls._relationship_fields(clazz, column_fields, namespace=namespace)
        return cls(name=cast(str, clazz.__name__), fields={**column_fields, **relationship_fields})
