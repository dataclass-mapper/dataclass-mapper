from dataclasses import dataclass
from dataclass_mapper.classmeta import ClassMeta
from dataclass_mapper.mapper import get_class_fields
from pydantic import BaseModel, validator, root_validator, Field, ConstrainedStr


def test_dataclass_has_no_validator():
    @dataclass
    class Dataclass:
        x: int

    assert not ClassMeta.from_class(Dataclass).has_validators


def test_pydantic_has_no_validators():
    class Pydantic1(BaseModel):
        x: int

    assert not ClassMeta.from_class(Pydantic1).has_validators


def test_pydantic_has_validators():
    class Pydantic1(BaseModel):
        x: int

        @validator('x')
        def val_x(cls, v):
            return v

    assert ClassMeta.from_class(Pydantic1).has_validators

    class Pydantic2(BaseModel):
        x: int

        @validator('*', pre=True)
        def val_x(cls, v):
            return v

    assert ClassMeta.from_class(Pydantic2).has_validators

    class Pydantic3(BaseModel):
        x: int
        y: int

        @validator('x', 'y')
        def val_x(cls, v):
            return v

    assert ClassMeta.from_class(Pydantic3).has_validators

    class Pydantic4(BaseModel):
        x: list[int]

        @validator('x', each_item=True)
        def val_x(cls, v):
            return v

    assert ClassMeta.from_class(Pydantic4).has_validators

    class Pydantic5(BaseModel):
        x: int

        @validator('x', pre=True, always=True)
        def val_x(cls, v):
            return v

    assert ClassMeta.from_class(Pydantic5).has_validators

    class Pydantic6(BaseModel):
        x: int

        @root_validator(pre=True)
        def check_root(cls, values):
            return values

    assert ClassMeta.from_class(Pydantic6).has_validators

    class Pydantic7(BaseModel):
        x: int

        @root_validator
        def check_root(cls, values):
            return values

    class Pydantic8(BaseModel):
        x: str = Field(max_length=5)

    class_meta_Pydantic8 = ClassMeta.from_class(Pydantic8)
    field_x_meta = get_class_fields(Pydantic8)["x"]
    assert not class_meta_Pydantic8.has_validators, "max_length is not a validator"
    assert field_x_meta.type is not str, "max_length changes the type of the field from str"
    assert field_x_meta.type is not ConstrainedStr, "to ConstrainedStr"
