import pytest
from pydantic import BaseModel

from dataclass_mapper.implementations.pydantic_v2 import PydanticV2ClassMeta, pydantic_version
from dataclass_mapper.namespace import Namespace

empty_namespace = Namespace(locals={}, globals={})

if pydantic_version() < (2, 0, 0):
    pytest.skip("V2 validators syntax", allow_module_level=True)

from pydantic import field_validator, model_validator  # noqa: E402


def test_pydantic_has_no_validators():
    class Pydantic1(BaseModel):
        x: int

    assert not PydanticV2ClassMeta.has_validators(Pydantic1)
    assert PydanticV2ClassMeta.from_clazz(Pydantic1, namespace=empty_namespace).use_construct


def test_pydantic_has_validators():
    class Pydantic1(BaseModel):
        x: int

        @field_validator("x")
        def val_x(cls, v):
            return v

    assert PydanticV2ClassMeta.has_validators(Pydantic1)
    assert not PydanticV2ClassMeta.from_clazz(Pydantic1, namespace=empty_namespace).use_construct

    class Pydantic2(BaseModel):
        x: int

        @field_validator("*", mode="before")
        def val_x(cls, v):
            return v

    assert PydanticV2ClassMeta.has_validators(Pydantic2)
    assert not PydanticV2ClassMeta.from_clazz(Pydantic2, namespace=empty_namespace).use_construct

    class Pydantic3(BaseModel):
        x: int
        y: int

        @field_validator("x", "y")
        def val_x(cls, v):
            return v

    assert PydanticV2ClassMeta.has_validators(Pydantic3)
    assert not PydanticV2ClassMeta.from_clazz(Pydantic3, namespace=empty_namespace).use_construct

    class Pydantic6(BaseModel):
        x: int

        @model_validator(mode="before")
        def check_root(cls, values):
            return values

    assert PydanticV2ClassMeta.has_validators(Pydantic6)
    assert not PydanticV2ClassMeta.from_clazz(Pydantic6, namespace=empty_namespace).use_construct

    class Pydantic7(BaseModel):
        x: int

        @model_validator(mode="after")  # type: ignore[arg-type]
        def check_root(cls, values):
            return values

    assert PydanticV2ClassMeta.has_validators(Pydantic7)
    assert not PydanticV2ClassMeta.from_clazz(Pydantic7, namespace=empty_namespace).use_construct

    # TODO;
    # This still registers a validator that is run with `Pydantic8(x="abcdef")`
    # and not with `Pydantic8.model_construc(x="abcdef")`
    # You can see the validator in `Pydantic8.__pydantic_validators__`, however it's a Rust object
    # and I can't easily access it.
    #
    # class Pydantic8(BaseModel):
    #     x: str = Field(max_length=5)
    #
    # assert PydanticV2ClassMeta.has_validators(Pydantic8), "max_length is a validator in v2"
    # assert not PydanticV2ClassMeta.from_clazz(Pydantic8, namespace=empty_namespace).use_construct
