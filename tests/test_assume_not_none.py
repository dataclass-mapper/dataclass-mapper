from dataclasses import dataclass
from typing import Dict, Optional

import pytest

from dataclass_mapper import assume_not_none, map_to, mapper


@dataclass
class Car:
    value: int
    color: str


def test_assume_not_none() -> None:
    @mapper(Car, {"value": assume_not_none("price"), "color": assume_not_none()})
    @dataclass
    class SportCar:
        price: Optional[int]
        color: Optional[str]

    assert map_to(SportCar(price=30_000, color="red"), Car) == Car(value=30000, color="red")


def test_assume_not_none_wrong_field() -> None:
    with pytest.raises(ValueError):

        @mapper(Car, {"value": assume_not_none(), "color": assume_not_none()})
        @dataclass
        class SportCar1:
            price: Optional[int]
            color: Optional[str]

    with pytest.raises(ValueError):

        @mapper(Car, {"value": assume_not_none("price"), "color": assume_not_none("abc")})
        @dataclass
        class SportCar2:
            price: Optional[int]
            color: Optional[str]


def test_assume_not_none_wrong_type() -> None:
    with pytest.raises(TypeError):

        @mapper(Car, {"value": assume_not_none("color"), "color": assume_not_none()})
        @dataclass
        class SportCar:
            price: Optional[int]
            color: Optional[str]
