from dataclasses import dataclass

from safe_mapper.safe_mapper import map_to, safe_mapper


@dataclass
class Person:
    first_name: str
    second_name: str


@dataclass
class Contract:
    person: Person
    signee: Person
    salary: int


def test_recursive_mapping():
    @safe_mapper(Person)
    @dataclass
    class Contact:
        first_name: str
        second_name: str

    @safe_mapper(Contract, {"person": "contact"})
    @dataclass
    class WorkContract:
        contact: Contact
        signee: Contact
        salary: int

    work_contract = WorkContract(
        contact=Contact("Desiree", "Petersen"),
        signee=Contact("Maci", "Krause"),
        salary=3000,
    )
    contract = Contract(
        person=Person("Desiree", "Petersen"),
        signee=Person("Maci", "Krause"),
        salary=3000,
    )
    assert map_to(work_contract, Contract) == contract
