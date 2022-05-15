# safe-mapper

Writing mapper methods between two similar data structures is boring and error-prone.
Much better to let a library auto-generate them for you.

This library makes sure that all fields of the target class are actually mapped to (already at the class definition time), and also provides helper mappers for variables that don't change their names.

## Installation

```
pip install safe-mapper
```

## Example

We have the following target data structure, a class `WorkContract` that contains an attribute of type `Person`.

```python
from dataclasses import dataclass

@dataclass
class Person:
    first_name: str
    second_name: str
    age: int

@dataclass
class WorkContract:
    worker: Person
    manager: Optional[Person]
    salary: int
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
        return Person(first_name=self.first_name, second_name=self.surname, age=self.age)
      
@dataclass
def SoftwareDeveloperContract:
    worker: ContactInfo
    manager: Optional[Person]
    salary: int

    def to_WorkContract(self) -> WorkContract:
        return WorkContract(
            worker=self.worker.to_Person(),
            manager=(None if self.manager is None else self.manager.to_Person()),
            salary=self.salary
        )


software_developer_contract: SoftwareDeveloperContract: 
work_contract = software_developer_contract.to_WorkContract
```

you can write:

```python
from safe_mapper.safe_mapper import map_to, safe_mapper

@safe_mapper(Person, {"second_name": "surname"})
@dataclass
class ContactInfo:
    first_name: str
    surname: str
    age: int
      
@safe_mapper(WorkContract)
@dataclass
def SoftwareDeveloperContract:
    worker: ContactInfo
    manager: Optional[Person]
    salary: int

software_developer_contract: SoftwareDeveloperContract: 
work_contract = map_to(software_developer_contract, WorkContract)
```

gives

```
Contact(first_name='Shakil', surname='Casey', age=35)
Person(first_name='Shakil', second_name='Casey', age=35)
```

## Features

The current version has support for:

- :heavy_check_mark: Python's `dataclass`
- :heavy_check_mark: `pydantic` classes, if installed with `pip install safe-mapper[pydantic]`
- :heavy_check_mark: Checking if all target fields are actually initialized.
  Raises a `ValueError` at class definition time when the type is different.
- :heavy_check_mark: Simple types (`str`, `int`, `float`, `datetime`, custom types) if the type on the target is the same.
  Raises a `TypeError` at class definition time when the type is different.
- :heavy_check_mark: `Optional` types.
  Raises a `TypeError` at class definition time when an optional type is mapped to a non-optional type.
- :heavy_check_mark: Recursive models
- :heavy_check_mark: `List` types
- :heavy_check_mark: Default values for simple types

Still missing features:

- :heavy_multiplication_x: `Union` types
- :heavy_multiplication_x: `Dict` types
- :heavy_multiplication_x: Default values for complicated types (for a mappable type)
- :heavy_multiplication_x: Aliases in `pydantic` classes
- :heavy_multiplication_x: Checking if all source attributes were used
- :heavy_multiplication_x: SQLAlchemy ORM
- :heavy_multiplication_x: Mapper in the other direction
