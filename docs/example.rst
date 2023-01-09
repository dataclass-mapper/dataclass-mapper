Large Example
=============

Given a target data structure, a class `WorkContract` that contains an attribute of type `Person`.

.. doctest::

   >>> from dataclasses import dataclass
   >>> from enum import Enum, auto
   >>> from typing import Optional
   >>>
   >>> @dataclass
   ... class Person:
   ...     first_name: str
   ...     second_name: str
   ...     full_name: str
   ...     age: int
   >>>
   >>> class Employment(Enum):
   ...     FULL_TIME = auto()
   ...     PART_TIME = auto()
   ...     EXTERNAL = auto()
   >>>
   >>> @dataclass
   ... class WorkContract:
   ...     worker: Person
   ...     manager: Optional[Person]
   ...     salary: int
   ...     signable: bool
   ...     employment: Employment
   ...     location: str

We want to have a mapper from the source data structure - ``SoftwareDeveloperContract`` with the attribute ``ContactInfo``.
Notice that the attribute ``second_name`` of ``Person`` is called ``surname`` in ``ContactInfo``.
Other than that, all the attribute names are the same.

Instead of writing:

.. doctest::

   >>> @dataclass
   ... class ContactInfo:
   ...     first_name: str
   ...     surname: str
   ...     age: int
   ...
   ...     def to_Person(self) -> Person:
   ...         return Person(
   ...             first_name=self.first_name,
   ...             second_name=self.surname,
   ...             full_name=f"{self.first_name} {self.surname}",
   ...             age=self.age,
   ...         )

   >>> class ContractType(str, Enum):
   ...     FULL_TIME = "FULL_TIME"
   ...     PART_TIME = "PART_TIME"
   ...     FREELANCER = "FREELANCER"
   ...     SUBCOMPANY = "SUBCOMPANY"
   ...
   ...     def to_Employment(self) -> Employment:
   ...         if self == ContractType.FULL_TIME:
   ...             return Employment.FULL_TIME
   ...         elif self == ContractType.PART_TIME:
   ...             return Employment.PART_TIME
   ...         else:
   ...             return Employment.EXTERNAL
   >>>
   >>> @dataclass
   ... class SoftwareDeveloperContract:
   ...     worker: ContactInfo
   ...     manager: Optional[ContactInfo]
   ...     salary: int
   ...     contract_type: ContractType
   ...
   ...     def to_WorkContract(self, location: str) -> WorkContract:
   ...         return WorkContract(
   ...             worker=self.worker.to_Person(),
   ...             manager=(None if self.manager is None else self.manager.to_Person()),
   ...             salary=self.salary,
   ...             signable=True,
   ...             employment=self.contract_type.to_Employment(),
   ...             location=location,
   ...         )
   >>>
   >>> software_developer_contract = SoftwareDeveloperContract(
   ...     worker=ContactInfo(first_name="John", surname="Page", age=30),
   ...     manager=ContactInfo(first_name="Jennifer", surname="Coulter", age=35),
   ...     salary=5000,
   ...     contract_type=ContractType.FULL_TIME,
   ... )
   >>> software_developer_contract.to_WorkContract(location="New York") #doctest: +NORMALIZE_WHITESPACE
   WorkContract(worker=Person(first_name='John', second_name='Page', full_name='John Page', age=30),
                manager=Person(first_name='Jennifer', second_name='Coulter', full_name='Jennifer Coulter', age=35),
                salary=5000,
                signable=True,
                employment=<Employment.FULL_TIME: 1>,
                location='New York')

you can write:

.. doctest::

   >>> from dataclass_mapper import map_to, mapper, enum_mapper, provide_with_extra
   >>>
   >>> @mapper(Person, {
   ...   "second_name": "surname",
   ...   "full_name": lambda self: f"{self.first_name} {self.surname}"
   ... })
   ... @dataclass
   ... class ContactInfo:
   ...     first_name: str
   ...     surname: str
   ...     age: int
   >>>
   >>> @enum_mapper(Employment, {"FREELANCER": Employment.EXTERNAL, "SUBCOMPANY": Employment.EXTERNAL})
   ... class ContractType(str, Enum):
   ...     FULL_TIME = "FULL_TIME"
   ...     PART_TIME = "PART_TIME"
   ...     FREELANCER = "FREELANCER"
   ...     SUBCOMPANY = "SUBCOMPANY"
   >>>       
   >>> @mapper(WorkContract, {"signable": lambda: True, "employment": "contract_type", "location": provide_with_extra()})
   ... @dataclass
   ... class SoftwareDeveloperContract:
   ...     worker: ContactInfo
   ...     manager: Optional[ContactInfo]
   ...     salary: int
   ...     contract_type: ContractType
   >>>
   >>> software_developer_contract = SoftwareDeveloperContract(
   ...     worker=ContactInfo(first_name="John", surname="Page", age=30),
   ...     manager=ContactInfo(first_name="Jennifer", surname="Coulter", age=35),
   ...     salary=5000,
   ...     contract_type=ContractType.FULL_TIME,
   ... )
   >>> map_to(software_developer_contract, WorkContract, extra={"location": "New York"}) #doctest: +NORMALIZE_WHITESPACE
   WorkContract(worker=Person(first_name='John', second_name='Page', full_name='John Page', age=30),
                manager=Person(first_name='Jennifer', second_name='Coulter', full_name='Jennifer Coulter', age=35),
                salary=5000,
                signable=True,
                employment=<Employment.FULL_TIME: 1>,
                location='New York')
