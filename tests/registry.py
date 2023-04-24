from enum import Enum


class FileRegistry(str, Enum):
    TEST_HEADER_INVALID_INPUT = 'test_header_invalid_input'
    TEST_BOOLEAN_INPUT = 'test_boolean_input'

    TEST_DATE_INPUT = 'test_date_input'
    TEST_DATE_INPUT_WRONG_RANGE = 'test_date_input_wrong_range'
    TEST_DATE_INPUT_WRONG_FORMAT = 'test_date_input_wrong_format'

    TEST_DATE_RANGE_INPUT = 'test_date_range_input'
