from dataclasses import dataclass

import pytest

from dataclass_mapper import map_to


@dataclass
class Foo:
    pass


@dataclass
class Bar:
    pass


def test_not_mappable_without_mapper_definition():
    with pytest.raises(NotImplementedError) as excinfo:
        map_to(Foo(), Bar)

    assert str(excinfo.value) == "Object of type 'Foo' cannot be mapped to 'Bar'"
