from typing import List

from pydantic import BaseModel, ConstrainedStr, Field, root_validator, validator

from dataclass_mapper.implementations.pydantic_v1 import PydanticV1ClassMeta
from dataclass_mapper.mapper import get_class_meta
from dataclass_mapper.namespace import Namespace

empty_namespace = Namespace(locals={}, globals={})


def test_pydantic_has_no_validators():
    class Pydantic1(BaseModel):
        x: int

    assert not PydanticV1ClassMeta.has_validators(Pydantic1)
    assert PydanticV1ClassMeta.from_clazz(Pydantic1, namespace=empty_namespace).use_construct


def test_pydantic_has_validators():
    class Pydantic1(BaseModel):
        x: int

        @validator("x")
        def val_x(cls, v):
            return v

    assert PydanticV1ClassMeta.has_validators(Pydantic1)
    assert not PydanticV1ClassMeta.from_clazz(Pydantic1, namespace=empty_namespace).use_construct

    class Pydantic2(BaseModel):
        x: int

        @validator("*", pre=True)
        def val_x(cls, v):
            return v

    assert PydanticV1ClassMeta.has_validators(Pydantic2)
    assert not PydanticV1ClassMeta.from_clazz(Pydantic2, namespace=empty_namespace).use_construct

    class Pydantic3(BaseModel):
        x: int
        y: int

        @validator("x", "y")
        def val_x(cls, v):
            return v

    assert PydanticV1ClassMeta.has_validators(Pydantic3)
    assert not PydanticV1ClassMeta.from_clazz(Pydantic3, namespace=empty_namespace).use_construct

    class Pydantic4(BaseModel):
        x: List[int]

        @validator("x", each_item=True)
        def val_x(cls, v):
            return v

    assert PydanticV1ClassMeta.has_validators(Pydantic4)
    assert not PydanticV1ClassMeta.from_clazz(Pydantic4, namespace=empty_namespace).use_construct

    class Pydantic5(BaseModel):
        x: int

        @validator("x", pre=True, always=True)
        def val_x(cls, v):
            return v

    assert PydanticV1ClassMeta.has_validators(Pydantic5)
    assert not PydanticV1ClassMeta.from_clazz(Pydantic5, namespace=empty_namespace).use_construct

    class Pydantic6(BaseModel):
        x: int

        @root_validator(pre=True)
        def check_root(cls, values):
            return values

    assert PydanticV1ClassMeta.has_validators(Pydantic6)
    assert not PydanticV1ClassMeta.from_clazz(Pydantic6, namespace=empty_namespace).use_construct

    class Pydantic7(BaseModel):
        x: int

        @root_validator
        def check_root(cls, values):
            return values

    assert PydanticV1ClassMeta.has_validators(Pydantic7)
    assert not PydanticV1ClassMeta.from_clazz(Pydantic7, namespace=empty_namespace).use_construct

    class Pydantic8(BaseModel):
        x: str = Field(max_length=5)

    class_meta_Pydantic8 = get_class_meta(Pydantic8, namespace=empty_namespace)
    field_x_meta = class_meta_Pydantic8.fields["x"]
    assert not PydanticV1ClassMeta.has_validators(Pydantic8), "max_length is not a validator"
    assert field_x_meta.type is not str, "max_length changes the type of the field from str"
    assert field_x_meta.type is not ConstrainedStr, "to ConstrainedStr"
