Large Example
=============

Given a target data structure, a class `WorkContract` that contains an attribute of type `Person`.

.. code-block:: python

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

We want to have a mapper from the source data structure - ``SoftwareDeveloperContract`` with the attribute ``ContactInfo``.
Notice that the attribute ``second_name`` of ``Person`` is called ``surname`` in ``ContactInfo``.
Other than that, all the attribute names are the same.

Instead of writing:

.. code-block:: python

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

you can write:

.. code-block:: python

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