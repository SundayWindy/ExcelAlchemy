from enum import Enum


class FileRegistry(str, Enum):
    TEST_HEADER_INVALID_INPUT = 'test_header_invalid_input.xlsx'
    TEST_BOOLEAN_INPUT = 'test_boolean_input.xlsx'

    TEST_DATE_INPUT = 'test_date_input.xlsx'
    TEST_DATE_INPUT_WRONG_FORMAT = 'test_date_input_wrong_format.xlsx'
