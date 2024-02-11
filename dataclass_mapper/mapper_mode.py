from enum import Enum


class MapperMode(Enum):
    """Enum that controlls which types of mappers should be created.
    By default it will create both a create and an update mapper.
    If the classes are however only used for one of the operations, it's best practice to limit the scope.
    Then an exception is thrown, if somebody uses the classes in an unintentional way.
    The MapperMode.UPDATE mode is also not as strict, when it comes to filling all fields
    (as the target object already has them filled).
    """

    CREATE = 1
    UPDATE = 2
    CREATE_AND_UPDATE = 3


MapperMode.CREATE.__doc__ = "only create a mapper for creating new objects"
MapperMode.UPDATE.__doc__ = "only create a mapper for updating existing objects"
MapperMode.CREATE_AND_UPDATE.__doc__ = "create mappers for both creating new objects and updating existing objects"
