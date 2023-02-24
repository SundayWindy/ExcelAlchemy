from excelalchemy.model.abstract import ABCValueType

EXCEL_CHOICE_VALUE_TYPE: dict[type[ABCValueType], type[ABCValueType]] = {}


def excel_choice(value_type: type[ABCValueType]) -> type[ABCValueType]:
    EXCEL_CHOICE_VALUE_TYPE[value_type] = value_type
    return value_type
