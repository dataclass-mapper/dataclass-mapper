# safe-mapper

A fast library to safely mapping between two classes.
It makes sure that all fields of the target class are actually mapped to (already at the class definition time), and also provides helper mappers for variables that don't change their names.
It checks the types of the fields and performs recursive mappings.

```python
from dataclasses import dataclass
from safe_mapper.safe_mapper import map_to, safe_mapper

@dataclass
class Person:
  first_name: str
  second_name: str
  age: int


@safe_mapper(Person, {"second_name": "surname"})
@dataclass
class Contact:
  first_name: str
  surname: str
  age: int


contact = Contact(first_name="Shakil", surname="Casey", age=35)
print(contact)
person = map_to(contact, Person)
print(person)
```

gives

```
Contact(first_name='Shakil', surname='Casey', age=35)
Person(first_name='Shakil', second_name='Casey', age=35)
```

In case if it's not possible to do the mapping (uninitialized field, ...), you will get an `ValueError` (at class definition time).
If some of the defined mappings use different types, you will get a `TypeError` (at class definition time).
If there is no mapper available, `map_to` will raise a `RuntimeError` when called.
