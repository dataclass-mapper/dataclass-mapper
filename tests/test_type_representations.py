from typing import Dict, List, Union

from dataclass_mapper.implementations.base import FieldMeta


def test_type_representations():
    int_fm = FieldMeta("name", type=int, allow_none=False, required=False)
    assert int_fm.type_string == "int"

    optional_int_fm = FieldMeta("name", type=int, allow_none=True, required=False)
    assert optional_int_fm.type_string == "Optional[int]"

    int_float_fm = FieldMeta("name", type=Union[int, float], allow_none=False, required=False)
    assert int_float_fm.type_string == "Union[int, float]"

    optional_int_float_fm = FieldMeta("name", type=Union[int, float], allow_none=True, required=False)
    assert optional_int_float_fm.type_string == "Union[int, float, NoneType]"

    list_int_fm = FieldMeta("name", type=List[int], allow_none=False, required=False)
    assert list_int_fm.type_string == "List[int]"

    optional_list_int_fm = FieldMeta("name", type=List[int], allow_none=True, required=False)
    assert optional_list_int_fm.type_string == "Optional[List[int]]"

    dict_str_int_fm = FieldMeta("name", type=Dict[str, int], allow_none=False, required=False)
    assert dict_str_int_fm.type_string == "Dict[str, int]"

    optional_dict_str_int_fm = FieldMeta("name", type=Dict[str, int], allow_none=True, required=False)
    assert optional_dict_str_int_fm.type_string == "Optional[Dict[str, int]]"
