

from dataclass_mapper.code_generator import AttributeLookup, DictLookup, Variable
from dataclass_mapper.expression_converters.expression_converter import map_expression
from dataclass_mapper.fieldtypes import OptionalFieldType, ListFieldType, ClassFieldType


def test_expression_converter():
    int_class_field_type = ClassFieldType(int)
    source = AttributeLookup("src", "x")

    assert str(map_expression(int_class_field_type, int_class_field_type, source)) == "src.x"

    assert str(map_expression(OptionalFieldType(int_class_field_type), OptionalFieldType(int_class_field_type), source)) == "None if src.x == None else src.x"

    assert str(map_expression(ListFieldType(int_class_field_type), ListFieldType(int_class_field_type), source)) == "[x for x in src.x]"
    # TODO: ^ optimization potential

    assert str(map_expression(ListFieldType(OptionalFieldType(int_class_field_type)), ListFieldType(OptionalFieldType(int_class_field_type)), source)) == "[None if x == None else x for x in src.x]"

    assert str(map_expression(ListFieldType(ListFieldType(int_class_field_type)), ListFieldType(ListFieldType(int_class_field_type)), source)) == "[[x for x in x] for x in src.x]"
    # TODO: wrong name
