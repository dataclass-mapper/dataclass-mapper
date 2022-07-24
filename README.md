# dataclass-mapper

Writing mapper methods between two similar dataclasses is boring and error-prone.
Much better to let a library auto-generate them for you.

This library makes sure that all fields of the target class are actually mapped to (already at the module import time), and also provides helper mappers for variables that don't change their names.
It supports Python's dataclasses and also Pydantic models.

## Installation

```
pip install dataclass-mapper
# or for Pydantic support
pip install dataclass-mapper[pydantic]
```

## Example

We have the following target data structure, a class `WorkContract` that contains an attribute of type `Person`.

```python
from dataclasses import dataclass

@dataclass
class Person:
    first_name: str
    second_name: str
    full_name: str
    age: int

@dataclass
class WorkContract:
    worker: Person
    manager: Optional[Person]
    salary: int
    signable: bool
```

We want to have a safe mapper from the source data structure - `SoftwareDeveloperContract` with the attribute `ContactInfo`.
Notice that the attribute `second_name` of `Person` is called `surname` in `ContactInfo`.
Other than that, all the attribute names are the same.

Instead of writing:

```python
@dataclass
class ContactInfo:
    first_name: str
    surname: str
    age: int

    def to_Person(self) -> Person:
        return Person(
            first_name=self.first_name,
            second_name=self.surname,
            full_name=f"{self.first_name} {self.surname}",
            age=self.age,
        )
      
@dataclass
class SoftwareDeveloperContract:
    worker: ContactInfo
    manager: Optional[ContactInfo]
    salary: int

    def to_WorkContract(self) -> WorkContract:
        return WorkContract(
            worker=self.worker.to_Person(),
            manager=(None if self.manager is None else self.manager.to_Person()),
            salary=self.salary,
            signable=True,
        )


software_developer_contract: SoftwareDeveloperContract
work_contract = software_developer_contract.to_WorkContract()
```

you can write:

```python
from dataclass_mapper import map_to, mapper

@mapper(Person, {
  "second_name": "surname",
  "full_name": lambda self: f"{self.first_name} {self.surname}"
})
@dataclass
class ContactInfo:
    first_name: str
    surname: str
    age: int
      
@mapper(WorkContract, {"signable": lambda: True})
@dataclass
class SoftwareDeveloperContract:
    worker: ContactInfo
    manager: Optional[ContactInfo]
    salary: int

software_developer_contract: SoftwareDeveloperContract
work_contract = map_to(software_developer_contract, WorkContract)
```

## Features

The current version has support for:

- :heavy_check_mark: Python's `dataclass`
- :heavy_check_mark: `pydantic` classes, if installed with `pip install dataclass-mapper[pydantic]`
- :heavy_check_mark: Checking if all target fields are actually initialized.
  Raises a `ValueError` at class definition time when the type is different.
- :heavy_check_mark: Simple types (`str`, `int`, `float`, `datetime`, custom types) if the type on the target is the same.
  Raises a `TypeError` at class definition time when the type is different.
- :heavy_check_mark: `Optional` types.
  Raises a `TypeError` at class definition time when an optional type is mapped to a non-optional type.
- :heavy_check_mark: Recursive models
- :heavy_check_mark: `List` types
- :heavy_check_mark: Default values for simple types
- :heavy_check_mark: Mapper in the other direction. Use the `mapper_from` decorator and the same `map_to` method.
- :heavy_check_mark: Assign Values with lambdas (with `{"x": lambda: 42}`)
- :heavy_check_mark: Assign Functions Calls with lambdas and `self` (with `{"x": lambda self: self.x}`)
- :heavy_check_mark: `USE_DEFAULT` for values that you don't wanna set but have a default value/factory

Still missing features:

- :heavy_multiplication_x: `Union` types
- :heavy_multiplication_x: `Dict` types
- :heavy_multiplication_x: Aliases in `pydantic` classes
- :heavy_multiplication_x: Checking if all source attributes were used
- :heavy_multiplication_x: SQLAlchemy ORM
